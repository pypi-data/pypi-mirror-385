import abc
import logging
from itertools import islice

from django.apps import apps
from django.contrib import contenttypes
from django.core.exceptions import FieldDoesNotExist

try:
    from django.core.exceptions import FullResultSet
except ImportError:

    class FullResultSet(Exception):
        pass


from django.db import connection, connections, transaction
from django.db.models import ManyToManyField, sql
from django.db.models.aggregates import Sum
from django.db.models.manager import Manager
from django.db.models.query_utils import Q
from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql.datastructures import Join
from django.db.models.sql.query import JoinInfo, Query
from django.db.models.sql.where import WhereNode

from denorm.contextmanagers import suppress_autotime

logger = logging.getLogger(__name__)


def many_to_many_pre_save(sender, instance, **kwargs):
    """
    Updates denormalised many-to-many fields for the model
    """
    if instance.pk:
        # Need a primary key to do m2m stuff
        for m2m in sender._meta.local_many_to_many:
            # This gets us all m2m fields, so limit it to just those that are denormed
            if hasattr(m2m, "denorm"):
                # Does some extra jiggery-pokery for "through" m2m models.
                # May not work under lots of conditions.
                try:
                    remote = m2m.remote_field  # Django>=1.10
                except AttributeError:
                    remote = m2m.rel
                if hasattr(remote, "through_model"):
                    # Clear exisiting through records (bit heavy handed?)
                    kwargs = {m2m.related.var_name: instance}

                    # Can't use m2m_column_name in a filter
                    # kwargs = { m2m.m2m_column_name(): instance.pk, }
                    remote.through_model.objects.filter(**kwargs).delete()

                    values = m2m.denorm.func(instance)
                    for value in values:
                        kwargs.update({m2m.m2m_reverse_name(): value.pk})
                        remote.through_model.objects.create(**kwargs)

                else:
                    values = m2m.denorm.func(instance)
                    try:
                        getattr(instance, m2m.attname).set(values)
                    except AttributeError:  # Django<1.10
                        setattr(instance, m2m.attname, values)


def many_to_many_post_save(sender, instance, created, **kwargs):
    if created:

        def check_resave():
            for m2m in sender._meta.local_many_to_many:
                if hasattr(m2m, "denorm"):
                    return True
            return False

        if check_resave():
            instance.save()


def get_alldenorms():
    """
    Get all denormalizations.
    """
    alldenorms = []
    for model in apps.get_models(include_auto_created=True):
        if not model._meta.proxy:
            for field in model._meta.fields:
                if hasattr(field, "denorm"):
                    if not field.denorm.model._meta.swapped:
                        alldenorms.append(field.denorm)
    return alldenorms


class Denorm:
    def __init__(self, skip=None, only=None):
        self.func = None
        self.skip = skip
        self.only = only

    def get_quote_name(self, using):
        if using:
            cconnection = connections[using]
        else:
            cconnection = connection
        return cconnection.ops.quote_name

    def setup(self, **kwargs):
        """
        Adds 'self' to the global denorm list
        and connects all needed signals.
        """

    def update(self, instance):
        """
        Updates the denormalizations in all instances in the queryset 'qs'.
        """

        # Get attribute name (required for denormalising ForeignKeys)
        field = instance._meta.get_field(self.fieldname)
        attname = field.attname

        attr = getattr(instance, attname)

        # only write new values to the DB if they actually changed
        new_value = self.func(instance)

        if isinstance(attr, Manager):
            # for a many to many field the decorated
            # function should return a list of either model instances
            # or primary keys
            old_pks = {x.pk for x in attr.all()}
            new_pks = set()

            for x in new_value:
                # we need to compare sets of objects based on pk values,
                # as django lacks an identity map.
                if hasattr(x, "pk"):
                    new_pks.add(x.pk)
                else:
                    new_pks.add(x)

            if old_pks != new_pks:
                setattr(instance, attname, new_value)
                return {}

        elif attr != new_value:
            if hasattr(field, "related_field") and isinstance(
                new_value, field.related_field.model
            ):
                setattr(instance, attname, None)
                setattr(instance, field.name, new_value)
            else:
                setattr(instance, attname, new_value)
            return {field.name: new_value}

    def get_triggers(self, using):
        return []


class BaseCallbackDenorm(Denorm):
    """
    Handles the denormalization of one field, using a python function
    as a callback.
    """

    def setup(self, **kwargs):
        """
        Calls setup() on all DenormDependency resolvers
        """
        super().setup(**kwargs)

        for dependency in self.depend:
            dependency.setup(self.model)

    def get_triggers(self, using):
        """
        Creates a list of all triggers needed to keep track of changes
        to fields this denorm depends on.
        """
        trigger_list = list()

        # Get the triggers of all DenormDependency instances attached
        # to our callback.
        for dependency in self.depend:
            trigger_list += dependency.get_triggers(using=using)
        ret = trigger_list + super().get_triggers(using=using)
        return ret


class CallbackDenorm(BaseCallbackDenorm):
    """
    As above, but with extra triggers on self as described below
    """

    def get_triggers(self, using):
        qn = self.get_quote_name(using)

        content_type = str(
            contenttypes.models.ContentType.objects.get_for_model(self.model).pk
        )

        # Create a trigger that marks any updated or newly created
        # instance of the model containing the denormalized field
        # as dirty.
        # This is only really needed if the instance was changed without
        # using the ORM or if it was part of a bulk update.
        # In those cases the self_save_handler won't get called by the
        # pre_save signal, so we need to ensure flush() does this later.
        from .db import triggers
        from .models import DirtyInstance

        action = triggers.TriggerActionInsert(
            model=DirtyInstance,
            columns=("content_type_id", "object_id"),
            values=(
                content_type,
                "NEW.%s" % qn(self.model._meta.pk.get_attname_column()[1]),
            ),
        )
        trigger_list = [
            triggers.Trigger(
                self.model,
                "after",
                "update",
                [action],
                content_type,
                using,
                self.skip,
                self.only,
            ),
            triggers.Trigger(
                self.model,
                "after",
                "insert",
                [action],
                content_type,
                using,
                self.skip,
                self.only,
            ),
        ]

        return trigger_list + super().get_triggers(using=using)


class BaseCacheKeyDenorm(Denorm):
    def __init__(self, depend_on_related, *args, **kwargs):
        self.depend = depend_on_related
        super().__init__(*args, **kwargs)
        import random

        self.func = lambda o: random.randint(-9223372036854775808, 9223372036854775807)

    def setup(self, **kwargs):
        """
        Calls setup() on all DenormDependency resolvers
        """
        super().setup(**kwargs)

        for dependency in self.depend:
            dependency.setup(self.model)

    def get_triggers(self, using):
        """
        Creates a list of all triggers needed to keep track of changes
        to fields this denorm depends on.
        """
        trigger_list = list()

        # Get the triggers of all DenormDependency instances attached
        # to our callback.
        for dependency in self.depend:
            trigger_list += dependency.get_triggers(using=using)

        return trigger_list + super().get_triggers(using=using)


class CacheKeyDenorm(BaseCacheKeyDenorm):
    """
    As above, but with extra triggers on self as described below
    """

    def get_triggers(self, using):
        qn = self.get_quote_name(using)

        content_type = str(
            contenttypes.models.ContentType.objects.get_for_model(self.model).pk
        )

        # This is only really needed if the instance was changed without
        # using the ORM or if it was part of a bulk update.
        # In those cases the self_save_handler won't get called by the
        # pre_save signal
        from .db import triggers

        action = triggers.TriggerActionUpdate(
            model=self.model,
            columns=(self.fieldname,),
            values=(triggers.RandomBigInt(),),
            where="%s = NEW.%s"
            % ((qn(self.model._meta.pk.get_attname_column()[1]),) * 2),
        )
        trigger_list = [
            triggers.Trigger(
                self.model,
                "after",
                "update",
                [action],
                content_type,
                using,
                self.skip,
                self.only,
            ),
            triggers.Trigger(
                self.model,
                "after",
                "insert",
                [action],
                content_type,
                using,
                self.skip,
                self.only,
            ),
        ]

        return trigger_list + super().get_triggers(using=using)


class TriggerWhereNode(WhereNode):
    def sql_for_columns(self, data, qn, connection, internal_type=None):
        """
        Returns the SQL fragment used for the left-hand side of a column
        constraint (for example, the "T1.foo" portion in the clause
        "WHERE ... T1.foo = 6").
        """
        table_alias, name, db_type = data
        if table_alias:
            if table_alias in ("NEW", "OLD"):
                lhs = f"{table_alias}.{qn(name)}"
            else:
                lhs = f"{qn(table_alias)}.{qn(name)}"
        else:
            lhs = qn(name)
        try:
            response = connection.ops.field_cast_sql(db_type, internal_type) % lhs
        except TypeError:
            response = connection.ops.field_cast_sql(db_type) % lhs
        return response


class TriggerFilterQuery(sql.Query):
    def __init__(self, model, trigger_alias, where=TriggerWhereNode):
        super().__init__(model, where)
        self.trigger_alias = trigger_alias
        try:

            class JoinField:
                def get_joining_columns(self):
                    return None

            join = Join(None, None, None, None, JoinField(), False)
        except BaseException:
            join = JoinInfo(None, None, None, None, ((None, None),), False, None)
        self.alias_map = {trigger_alias: join}

    def get_initial_alias(self):
        return self.trigger_alias


class AggregateDenorm(Denorm):
    __metaclass__ = abc.ABCMeta

    def __init__(self, skip=None, only=None):
        self.manager = None
        self.skip = skip
        self.only = only

    def setup(self, sender, **kwargs):
        # as we connected to the ``class_prepared`` signal for any sender
        # and we only need to setup once, check if the sender is our model.
        if sender is self.model:
            super().setup(sender=sender, **kwargs)

        # related managers will only be available after both models are initialized
        # so check if its available already, and get our manager
        if not self.manager and hasattr(self.model, str(self.manager_name)):
            self.manager = getattr(self.model, self.manager_name)

    def get_related_where(self, fk_name, using, type):
        qn = self.get_quote_name(using)

        related_where = [
            "%s = %s.%s"
            % (qn(self.model._meta.pk.get_attname_column()[1]), type, qn(fk_name))
        ]
        related_query = Query(self.manager.related.model)
        for name, value in self.filter.items():
            related_query.add_q(Q(**{name: value}))
        for name, value in self.exclude.items():
            related_query.add_q(~Q(**{name: value}))
        related_query.add_extra(
            None,
            None,
            [
                "%s = %s.%s"
                % (
                    qn(self.model._meta.pk.get_attname_column()[1]),
                    type,
                    qn(self.manager.related.field.m2m_column_name()),
                )
            ],
            None,
            None,
            None,
        )
        related_query.add_count_column()
        related_query.clear_ordering(force_empty=True)
        related_query.default_cols = False
        related_filter_where, related_where_params = related_query.get_compiler(
            using=using
        ).as_sql()
        if related_filter_where is not None:
            related_where.append("(" + related_filter_where + ") > 0")
        return related_where, related_where_params

    def m2m_triggers(self, content_type, fk_name, related_field, using):
        """
        Returns triggers for m2m relation
        """
        from .db import triggers

        related_inc_where, _ = self.get_related_where(fk_name, using, "NEW")
        related_dec_where, related_where_params = self.get_related_where(
            fk_name, using, "OLD"
        )
        related_increment = triggers.TriggerActionUpdate(
            model=self.model,
            columns=(self.fieldname,),
            values=(self.get_related_increment_value(using),),
            where=(" AND ".join(related_inc_where), related_where_params),
        )
        related_decrement = triggers.TriggerActionUpdate(
            model=self.model,
            columns=(self.fieldname,),
            values=(self.get_related_decrement_value(using),),
            where=(" AND ".join(related_dec_where), related_where_params),
        )
        trigger_list = [
            triggers.Trigger(
                related_field,
                "after",
                "update",
                [related_increment, related_decrement],
                content_type,
                using,
                self.skip,
            ),
            triggers.Trigger(
                related_field,
                "after",
                "insert",
                [related_increment],
                content_type,
                using,
                self.skip,
            ),
            triggers.Trigger(
                related_field,
                "after",
                "delete",
                [related_decrement],
                content_type,
                using,
                self.skip,
            ),
        ]
        return trigger_list

    def get_triggers(self, using):
        from .db import triggers

        if using:
            cconnection = connections[using]
        else:
            cconnection = connection

        qn = self.get_quote_name(using)

        try:  # Django>=1.9
            related_field = self.manager.field
        except AttributeError:
            related_field = self.manager.related.field
        if isinstance(related_field, ManyToManyField):
            fk_name = related_field.m2m_reverse_name()
            inc_where = [
                "%(id)s IN (SELECT %(reverse_related)s FROM %(m2m_table)s WHERE %(related)s = NEW.%(id)s)"
                % {
                    "id": qn(self.model._meta.pk.get_attname_column()[0]),
                    "related": qn(related_field.m2m_column_name()),
                    "m2m_table": qn(related_field.m2m_db_table()),
                    "reverse_related": qn(fk_name),
                }
            ]
            dec_where = [action.replace("NEW.", "OLD.") for action in inc_where]
        else:
            pk_name = qn(self.model._meta.pk.get_attname_column()[1])
            fk_name = qn(related_field.attname)
            inc_where = [f"{pk_name} = NEW.{fk_name}"]
            dec_where = [f"{pk_name} = OLD.{fk_name}"]

        content_type = str(
            contenttypes.models.ContentType.objects.get_for_model(self.model).pk
        )

        if hasattr(self.manager, "field"):  # Django>=1.9
            related_model = self.manager.field.model
        else:  # Django>=1.8
            related_model = self.manager.related.related_model
        inc_query = TriggerFilterQuery(related_model, trigger_alias="NEW")
        inc_query.add_q(Q(**self.filter))
        inc_query.add_q(~Q(**self.exclude))
        qn = SQLCompiler(inc_query, cconnection, using)
        try:
            inc_filter_where, _ = inc_query.where.as_sql(qn, cconnection)
        except FullResultSet:
            inc_filter_where, _ = ("", "")

        dec_query = TriggerFilterQuery(related_model, trigger_alias="OLD")
        dec_query.add_q(Q(**self.filter))
        dec_query.add_q(~Q(**self.exclude))
        qn = SQLCompiler(dec_query, cconnection, using)
        try:
            dec_filter_where, where_params = dec_query.where.as_sql(qn, cconnection)
        except FullResultSet:
            dec_filter_where, where_params = ("", "")

        if inc_filter_where:
            inc_where.append(inc_filter_where)
        if dec_filter_where:
            dec_where.append(dec_filter_where)
            # create the triggers for the incremental updates
        increment = triggers.TriggerActionUpdate(
            model=self.model,
            columns=(self.fieldname,),
            values=(self.get_increment_value(using),),
            where=(" AND ".join(inc_where), where_params),
        )
        decrement = triggers.TriggerActionUpdate(
            model=self.model,
            columns=(self.fieldname,),
            values=(self.get_decrement_value(using),),
            where=(" AND ".join(dec_where), where_params),
        )

        trigger_list = [
            triggers.Trigger(
                related_model,
                "after",
                "update",
                [increment, decrement],
                content_type,
                using,
                self.skip,
            ),
            triggers.Trigger(
                related_model,
                "after",
                "insert",
                [increment],
                content_type,
                using,
                self.skip,
            ),
            triggers.Trigger(
                related_model,
                "after",
                "delete",
                [decrement],
                content_type,
                using,
                self.skip,
            ),
        ]
        if isinstance(related_field, ManyToManyField):
            trigger_list.extend(
                self.m2m_triggers(content_type, fk_name, related_field, using)
            )
        return trigger_list

    @abc.abstractmethod
    def get_increment_value(self, using):
        """
        Returns SQL for incrementing value
        """

    @abc.abstractmethod
    def get_decrement_value(self, using):
        """
        Returns SQL for decrementing value
        """


class SumDenorm(AggregateDenorm):
    """
    Handles denormalization of a sum field by doing incrementally updates.
    """

    def __init__(self, skip=None, field=None):
        super().__init__(skip)
        # in case we want to set the value without relying on the
        # correctness of the incremental updates we create a function that
        # calculates it from scratch.
        self.sum_field = field
        self.func = lambda obj: (
            getattr(obj, self.manager_name)
            .filter(**self.filter)
            .exclude(**self.exclude)
            .aggregate(Sum(self.sum_field))
            .values()[0]
            or 0
        )

    def get_increment_value(self, using):
        qn = self.get_quote_name(using)

        return f"{qn(self.fieldname)} + NEW.{qn(self.sum_field)}"

    def get_decrement_value(self, using):
        qn = self.get_quote_name(using)

        return f"{qn(self.fieldname)} - OLD.{qn(self.sum_field)}"

    def get_related_increment_value(self, using):
        qn = self.get_quote_name(using)

        related_query = Query(self.manager.related.model)
        related_query.add_extra(
            None,
            None,
            [
                "%s = %s.%s"
                % (
                    qn(self.model._meta.pk.get_attname_column()[1]),
                    "NEW",
                    qn(self.manager.related.field.m2m_column_name()),
                )
            ],
            None,
            None,
            None,
        )
        related_query.add_fields([self.fieldname])
        related_query.clear_ordering(force_empty=True)
        related_query.default_cols = False
        related_filter_where, related_where_params = related_query.get_compiler(
            using=using
        ).as_sql()
        return f"{qn(self.fieldname)} + ({related_filter_where})"

    def get_related_decrement_value(self, using):
        qn = self.get_quote_name(using)

        related_query = Query(self.manager.related.model)
        related_query.add_extra(
            None,
            None,
            [
                "%s = %s.%s"
                % (
                    qn(self.model._meta.pk.get_attname_column()[1]),
                    "OLD",
                    qn(self.manager.related.field.m2m_column_name()),
                )
            ],
            None,
            None,
            None,
        )
        related_query.add_fields([self.fieldname])
        related_query.clear_ordering(force_empty=True)
        related_query.default_cols = False
        related_filter_where, related_where_params = related_query.get_compiler(
            using=using
        ).as_sql()
        return f"{qn(self.fieldname)} - ({related_filter_where})"


class CountDenorm(AggregateDenorm):
    """
    Handles the denormalization of a count field by doing incrementally
    updates.
    """

    def __init__(self, skip=None, only=None):
        super().__init__(skip=skip, only=only)
        # in case we want to set the value without relying on the
        # correctness of the incremental updates we create a function that
        # calculates it from scratch.
        self.func = (
            lambda obj: getattr(obj, self.manager_name)
            .filter(**self.filter)
            .exclude(**self.exclude)
            .count()
        )

    def get_increment_value(self, using):
        qn = self.get_quote_name(using)

        return "%s + 1" % qn(self.fieldname)

    def get_decrement_value(self, using):
        qn = self.get_quote_name(using)

        return "%s - 1" % qn(self.fieldname)

    def get_related_increment_value(self, using):
        return self.get_increment_value(using)

    def get_related_decrement_value(self, using):
        return self.get_decrement_value(using)


def rebuild_instances_of(model, *args, **kwargs):
    # create DirtyInstance for all models

    from denorm.conf import settings

    from .models import DirtyInstance

    content_type = contenttypes.models.ContentType.objects.get_for_model(model)
    objs = (
        DirtyInstance(content_type=content_type, object_id=pk)
        for pk in model.objects.filter(*args, **kwargs).values_list("pk", flat=True)
    )

    while True:
        batch = list(islice(objs, settings.DENORM_BATCH_SIZE))
        if not batch:
            break
        DirtyInstance.objects.bulk_create(batch, settings.DENORM_BATCH_SIZE)


def rebuildall(model_name=None, field_name=None, verbose=False, flush_=True):
    """
    Updates all models containing denormalized fields.
    """

    alldenorms = get_alldenorms()
    models = {}
    for denorm in alldenorms:
        current_app_label = denorm.model._meta.app_label
        current_model_name = denorm.model._meta.model.__name__
        current_app_model = f"{current_app_label}.{current_model_name}"
        if model_name is None or model_name.lower() in (
            current_app_label.lower(),
            current_model_name.lower(),
            current_app_model.lower(),
        ):
            if field_name is None or field_name == denorm.fieldname:
                models.setdefault(denorm.model, []).append(denorm)

    i = 0
    for model, denorms in models.items():
        if verbose:
            for denorm in denorms:
                msg = (
                    "making dirty instances",
                    f"{i + 1}/{len(alldenorms)}",
                    denorm.fieldname,
                    "in",
                    denorm.model,
                )
                logger.info(msg)
                i += 1

        rebuild_instances_of(model)

    if flush_:
        flush(verbose)


def drop_triggers(using=None):
    from .db import triggers

    triggerset = triggers.TriggerSet(using=using)
    triggerset.drop()


def install_triggers(using=None):
    """
    Installs all required triggers in the database
    """
    build_triggerset(using=using).install()


def build_triggerset(using=None):
    from .db import triggers

    alldenorms = get_alldenorms()

    # Use a TriggerSet to ensure each event gets just one trigger
    triggerset = triggers.TriggerSet(using=using)
    for denorm in alldenorms:
        triggerset.append(denorm.get_triggers(using=using))
    return triggerset


INTERACTIVE = False


def flush_single(content_type_id, object_id, content_type=None):
    from denorm.conf import settings

    from .models import DirtyInstance

    disable_autotime_during_flush = settings.DENORM_DISABLE_AUTOTIME_DURING_FLUSH
    autotime_field_names = settings.DENORM_AUTOTIME_FIELD_NAMES

    if content_type is None:
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get(pk=content_type_id)

    with transaction.atomic():
        res = DirtyInstance.objects.filter(
            content_type_id=content_type.pk, object_id=object_id
        ).select_for_update(skip_locked=True)

        if not res.exists():
            return

        klass = content_type.model_class()
        try:
            obj = klass.objects.select_for_update(of=("self",), skip_locked=True).get(
                pk=object_id
            )
        except klass.DoesNotExist:
            res.delete()
            return

        if obj is None:
            # nowait=True raises OperationalError when row is locked, skip this update
            return

        func_names = set(list(res.values_list("func_name", flat=True)))

        # At this point, all_func_names contains an iterable with all
        # func_names attributes requested re-indexing.
        kw = {}

        # If there's a None in it, we might as well save the whole object without any filtering.
        # If there is no None, we need to take all the functions that need rebuilding and update
        # but only those parameters.
        if None not in func_names:
            # If not, we want to pass a list of all updated fields to update_fields,
            # but first we need to check if they're callable and present on the object.
            update_fields = []
            for func_name in func_names:
                try:
                    obj._meta.get_field(func_name)
                    update_fields.append(func_name)
                except FieldDoesNotExist:
                    continue

            if update_fields:
                kw = dict(update_fields=update_fields)

        if disable_autotime_during_flush:
            with suppress_autotime(obj, autotime_field_names):
                obj.save(**kw)
        else:
            obj.save(**kw)

        res.delete()


def flush(run_once=False):
    """
    Updates all model instances marked as dirty by the DirtyInstance
    model.
    After this method finishes the DirtyInstance table is empty and
    all denormalized fields have consistent data.
    """

    # Loop until break.
    # We may need multiple passes, because an update on one instance
    # may cause an other instance to be marked dirty (dependency chains)

    # Get all dirty markers

    ran_once = False

    from .models import DirtyInstance

    while True:
        if run_once and ran_once:
            break

        processed = 0
        for content_type_id, object_id in (
            DirtyInstance.objects.all()
            .values_list("content_type_id", "object_id")
            .distinct()
        ):
            flush_single(content_type_id, object_id)
            processed += 1

        if not processed:
            return

        ran_once = True
