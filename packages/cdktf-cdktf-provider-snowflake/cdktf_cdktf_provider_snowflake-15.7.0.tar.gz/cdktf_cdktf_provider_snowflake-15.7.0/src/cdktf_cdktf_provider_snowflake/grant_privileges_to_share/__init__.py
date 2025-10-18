r'''
# `snowflake_grant_privileges_to_share`

Refer to the Terraform Registry for docs: [`snowflake_grant_privileges_to_share`](https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class GrantPrivilegesToShare(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.grantPrivilegesToShare.GrantPrivilegesToShare",
):
    '''Represents a {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share snowflake_grant_privileges_to_share}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        privileges: typing.Sequence[builtins.str],
        to_share: builtins.str,
        id: typing.Optional[builtins.str] = None,
        on_all_tables_in_schema: typing.Optional[builtins.str] = None,
        on_database: typing.Optional[builtins.str] = None,
        on_function: typing.Optional[builtins.str] = None,
        on_schema: typing.Optional[builtins.str] = None,
        on_table: typing.Optional[builtins.str] = None,
        on_tag: typing.Optional[builtins.str] = None,
        on_view: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GrantPrivilegesToShareTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share snowflake_grant_privileges_to_share} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param privileges: The privileges to grant on the share. See available list of privileges: https://docs.snowflake.com/en/sql-reference/sql/grant-privilege-share#syntax. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#privileges GrantPrivilegesToShare#privileges}
        :param to_share: The fully qualified name of the share on which privileges will be granted. For more information about this resource, see `docs <./share>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#to_share GrantPrivilegesToShare#to_share}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#id GrantPrivilegesToShare#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param on_all_tables_in_schema: The fully qualified identifier for the schema for which the specified privilege will be granted for all tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_all_tables_in_schema GrantPrivilegesToShare#on_all_tables_in_schema}
        :param on_database: The fully qualified name of the database on which privileges will be granted. For more information about this resource, see `docs <./database>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_database GrantPrivilegesToShare#on_database}
        :param on_function: The fully qualified name of the function on which privileges will be granted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_function GrantPrivilegesToShare#on_function}
        :param on_schema: The fully qualified name of the schema on which privileges will be granted. For more information about this resource, see `docs <./schema>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_schema GrantPrivilegesToShare#on_schema}
        :param on_table: The fully qualified name of the table on which privileges will be granted. For more information about this resource, see `docs <./table>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_table GrantPrivilegesToShare#on_table}
        :param on_tag: The fully qualified name of the tag on which privileges will be granted. For more information about this resource, see `docs <./tag>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_tag GrantPrivilegesToShare#on_tag}
        :param on_view: The fully qualified name of the view on which privileges will be granted. For more information about this resource, see `docs <./view>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_view GrantPrivilegesToShare#on_view}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#timeouts GrantPrivilegesToShare#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204f570a41eb3c8ab007b93a7be873e976b075f7f4ce4859077282275504c616)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GrantPrivilegesToShareConfig(
            privileges=privileges,
            to_share=to_share,
            id=id,
            on_all_tables_in_schema=on_all_tables_in_schema,
            on_database=on_database,
            on_function=on_function,
            on_schema=on_schema,
            on_table=on_table,
            on_tag=on_tag,
            on_view=on_view,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a GrantPrivilegesToShare resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GrantPrivilegesToShare to import.
        :param import_from_id: The id of the existing GrantPrivilegesToShare that should be imported. Refer to the {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GrantPrivilegesToShare to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59cea26894888819e5d3a518177002a860d0f6713cc39693e36bb5a1309c1cd9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#create GrantPrivilegesToShare#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#delete GrantPrivilegesToShare#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#read GrantPrivilegesToShare#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#update GrantPrivilegesToShare#update}.
        '''
        value = GrantPrivilegesToShareTimeouts(
            create=create, delete=delete, read=read, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOnAllTablesInSchema")
    def reset_on_all_tables_in_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnAllTablesInSchema", []))

    @jsii.member(jsii_name="resetOnDatabase")
    def reset_on_database(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDatabase", []))

    @jsii.member(jsii_name="resetOnFunction")
    def reset_on_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnFunction", []))

    @jsii.member(jsii_name="resetOnSchema")
    def reset_on_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnSchema", []))

    @jsii.member(jsii_name="resetOnTable")
    def reset_on_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnTable", []))

    @jsii.member(jsii_name="resetOnTag")
    def reset_on_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnTag", []))

    @jsii.member(jsii_name="resetOnView")
    def reset_on_view(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnView", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GrantPrivilegesToShareTimeoutsOutputReference":
        return typing.cast("GrantPrivilegesToShareTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="onAllTablesInSchemaInput")
    def on_all_tables_in_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onAllTablesInSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="onDatabaseInput")
    def on_database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onDatabaseInput"))

    @builtins.property
    @jsii.member(jsii_name="onFunctionInput")
    def on_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onFunctionInput"))

    @builtins.property
    @jsii.member(jsii_name="onSchemaInput")
    def on_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="onTableInput")
    def on_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onTableInput"))

    @builtins.property
    @jsii.member(jsii_name="onTagInput")
    def on_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onTagInput"))

    @builtins.property
    @jsii.member(jsii_name="onViewInput")
    def on_view_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onViewInput"))

    @builtins.property
    @jsii.member(jsii_name="privilegesInput")
    def privileges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "privilegesInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GrantPrivilegesToShareTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GrantPrivilegesToShareTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="toShareInput")
    def to_share_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toShareInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99cfe0f35561e2f0be61d97d9eb4e45509d099db3f1074af7a2d53ba5f63ad2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onAllTablesInSchema")
    def on_all_tables_in_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onAllTablesInSchema"))

    @on_all_tables_in_schema.setter
    def on_all_tables_in_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36ab90cdbadbdad3a61909f485ff63bb7f35baa6659210ac989a56643791b905)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onAllTablesInSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onDatabase")
    def on_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onDatabase"))

    @on_database.setter
    def on_database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__948b241207a85edab1eff75ff9db1649c6087e5f35a059840cac69057807dd10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onDatabase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onFunction")
    def on_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onFunction"))

    @on_function.setter
    def on_function(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32d073d15be8f6a890916b6ebea8c146491e54b72a42918ba3e915e35b1b0257)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onFunction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onSchema")
    def on_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onSchema"))

    @on_schema.setter
    def on_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c505c8350be84d542df63c04ea49b8ae5c26971a013cd695c7dcb576365e6050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onTable")
    def on_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onTable"))

    @on_table.setter
    def on_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e70d399249ba821daffb8ebbfc3b127051ade2a977597320d721340966a01494)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onTag")
    def on_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onTag"))

    @on_tag.setter
    def on_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c9b6f75f28c7f8b4a02639cd7ef1d0631eb11321f390f8acb1f92a182d4961f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onView")
    def on_view(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onView"))

    @on_view.setter
    def on_view(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__807719716677fceabdf4f43f79140a3724b39b74a548c1eb9e43483885b242c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onView", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privileges")
    def privileges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "privileges"))

    @privileges.setter
    def privileges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b04a967a791af1910930aa1cae37a53077bd98699d7eea09d42b5626fa6b7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privileges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toShare")
    def to_share(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "toShare"))

    @to_share.setter
    def to_share(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43b7a5a28d67aee81b8172f89f0b8cc74d713b0a87c786440962e1036195103)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toShare", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.grantPrivilegesToShare.GrantPrivilegesToShareConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "privileges": "privileges",
        "to_share": "toShare",
        "id": "id",
        "on_all_tables_in_schema": "onAllTablesInSchema",
        "on_database": "onDatabase",
        "on_function": "onFunction",
        "on_schema": "onSchema",
        "on_table": "onTable",
        "on_tag": "onTag",
        "on_view": "onView",
        "timeouts": "timeouts",
    },
)
class GrantPrivilegesToShareConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        privileges: typing.Sequence[builtins.str],
        to_share: builtins.str,
        id: typing.Optional[builtins.str] = None,
        on_all_tables_in_schema: typing.Optional[builtins.str] = None,
        on_database: typing.Optional[builtins.str] = None,
        on_function: typing.Optional[builtins.str] = None,
        on_schema: typing.Optional[builtins.str] = None,
        on_table: typing.Optional[builtins.str] = None,
        on_tag: typing.Optional[builtins.str] = None,
        on_view: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GrantPrivilegesToShareTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param privileges: The privileges to grant on the share. See available list of privileges: https://docs.snowflake.com/en/sql-reference/sql/grant-privilege-share#syntax. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#privileges GrantPrivilegesToShare#privileges}
        :param to_share: The fully qualified name of the share on which privileges will be granted. For more information about this resource, see `docs <./share>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#to_share GrantPrivilegesToShare#to_share}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#id GrantPrivilegesToShare#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param on_all_tables_in_schema: The fully qualified identifier for the schema for which the specified privilege will be granted for all tables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_all_tables_in_schema GrantPrivilegesToShare#on_all_tables_in_schema}
        :param on_database: The fully qualified name of the database on which privileges will be granted. For more information about this resource, see `docs <./database>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_database GrantPrivilegesToShare#on_database}
        :param on_function: The fully qualified name of the function on which privileges will be granted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_function GrantPrivilegesToShare#on_function}
        :param on_schema: The fully qualified name of the schema on which privileges will be granted. For more information about this resource, see `docs <./schema>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_schema GrantPrivilegesToShare#on_schema}
        :param on_table: The fully qualified name of the table on which privileges will be granted. For more information about this resource, see `docs <./table>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_table GrantPrivilegesToShare#on_table}
        :param on_tag: The fully qualified name of the tag on which privileges will be granted. For more information about this resource, see `docs <./tag>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_tag GrantPrivilegesToShare#on_tag}
        :param on_view: The fully qualified name of the view on which privileges will be granted. For more information about this resource, see `docs <./view>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_view GrantPrivilegesToShare#on_view}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#timeouts GrantPrivilegesToShare#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = GrantPrivilegesToShareTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5dc87562d29cd935055c6310cbf416df91caa02a79f0f39caa35c880965f49f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument privileges", value=privileges, expected_type=type_hints["privileges"])
            check_type(argname="argument to_share", value=to_share, expected_type=type_hints["to_share"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument on_all_tables_in_schema", value=on_all_tables_in_schema, expected_type=type_hints["on_all_tables_in_schema"])
            check_type(argname="argument on_database", value=on_database, expected_type=type_hints["on_database"])
            check_type(argname="argument on_function", value=on_function, expected_type=type_hints["on_function"])
            check_type(argname="argument on_schema", value=on_schema, expected_type=type_hints["on_schema"])
            check_type(argname="argument on_table", value=on_table, expected_type=type_hints["on_table"])
            check_type(argname="argument on_tag", value=on_tag, expected_type=type_hints["on_tag"])
            check_type(argname="argument on_view", value=on_view, expected_type=type_hints["on_view"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "privileges": privileges,
            "to_share": to_share,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id
        if on_all_tables_in_schema is not None:
            self._values["on_all_tables_in_schema"] = on_all_tables_in_schema
        if on_database is not None:
            self._values["on_database"] = on_database
        if on_function is not None:
            self._values["on_function"] = on_function
        if on_schema is not None:
            self._values["on_schema"] = on_schema
        if on_table is not None:
            self._values["on_table"] = on_table
        if on_tag is not None:
            self._values["on_tag"] = on_tag
        if on_view is not None:
            self._values["on_view"] = on_view
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def privileges(self) -> typing.List[builtins.str]:
        '''The privileges to grant on the share. See available list of privileges: https://docs.snowflake.com/en/sql-reference/sql/grant-privilege-share#syntax.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#privileges GrantPrivilegesToShare#privileges}
        '''
        result = self._values.get("privileges")
        assert result is not None, "Required property 'privileges' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def to_share(self) -> builtins.str:
        '''The fully qualified name of the share on which privileges will be granted.

        For more information about this resource, see `docs <./share>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#to_share GrantPrivilegesToShare#to_share}
        '''
        result = self._values.get("to_share")
        assert result is not None, "Required property 'to_share' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#id GrantPrivilegesToShare#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_all_tables_in_schema(self) -> typing.Optional[builtins.str]:
        '''The fully qualified identifier for the schema for which the specified privilege will be granted for all tables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_all_tables_in_schema GrantPrivilegesToShare#on_all_tables_in_schema}
        '''
        result = self._values.get("on_all_tables_in_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_database(self) -> typing.Optional[builtins.str]:
        '''The fully qualified name of the database on which privileges will be granted.

        For more information about this resource, see `docs <./database>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_database GrantPrivilegesToShare#on_database}
        '''
        result = self._values.get("on_database")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_function(self) -> typing.Optional[builtins.str]:
        '''The fully qualified name of the function on which privileges will be granted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_function GrantPrivilegesToShare#on_function}
        '''
        result = self._values.get("on_function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_schema(self) -> typing.Optional[builtins.str]:
        '''The fully qualified name of the schema on which privileges will be granted.

        For more information about this resource, see `docs <./schema>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_schema GrantPrivilegesToShare#on_schema}
        '''
        result = self._values.get("on_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_table(self) -> typing.Optional[builtins.str]:
        '''The fully qualified name of the table on which privileges will be granted.

        For more information about this resource, see `docs <./table>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_table GrantPrivilegesToShare#on_table}
        '''
        result = self._values.get("on_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_tag(self) -> typing.Optional[builtins.str]:
        '''The fully qualified name of the tag on which privileges will be granted.

        For more information about this resource, see `docs <./tag>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_tag GrantPrivilegesToShare#on_tag}
        '''
        result = self._values.get("on_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_view(self) -> typing.Optional[builtins.str]:
        '''The fully qualified name of the view on which privileges will be granted.

        For more information about this resource, see `docs <./view>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#on_view GrantPrivilegesToShare#on_view}
        '''
        result = self._values.get("on_view")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GrantPrivilegesToShareTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#timeouts GrantPrivilegesToShare#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GrantPrivilegesToShareTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GrantPrivilegesToShareConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-snowflake.grantPrivilegesToShare.GrantPrivilegesToShareTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "delete": "delete",
        "read": "read",
        "update": "update",
    },
)
class GrantPrivilegesToShareTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#create GrantPrivilegesToShare#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#delete GrantPrivilegesToShare#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#read GrantPrivilegesToShare#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#update GrantPrivilegesToShare#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f0d63e40266bfe497e3f4a0bfb06d4ad83792ee513f729932dc6b29aea908be)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if read is not None:
            self._values["read"] = read
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#create GrantPrivilegesToShare#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#delete GrantPrivilegesToShare#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#read GrantPrivilegesToShare#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/snowflakedb/snowflake/2.9.0/docs/resources/grant_privileges_to_share#update GrantPrivilegesToShare#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GrantPrivilegesToShareTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GrantPrivilegesToShareTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-snowflake.grantPrivilegesToShare.GrantPrivilegesToShareTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f41afdb8e8e1444fc8cda5292bf226cd850443d756a70ceffa55d6700b842f1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetRead")
    def reset_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRead", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__379a2ab8aa25135c928359aae45836bcf13abe8054aac6d9c013da4937add143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab22b3fb153e18ee7ce4978ea9e60f2efcb5d677ad79d145382b9259cbb696d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__423440895de1f51c79e33cf3de78bca1fb7f98b969d596294d3d963f16a416ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44f983329e880120661c9d1fbccd7a7af900d2ebffc93e9b9c9a34c4aea89068)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GrantPrivilegesToShareTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GrantPrivilegesToShareTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GrantPrivilegesToShareTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48df736c84c1fc335ef5b08ebbf512a263a20b6fa6c9f7378ce5373271fbe08d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GrantPrivilegesToShare",
    "GrantPrivilegesToShareConfig",
    "GrantPrivilegesToShareTimeouts",
    "GrantPrivilegesToShareTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__204f570a41eb3c8ab007b93a7be873e976b075f7f4ce4859077282275504c616(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    privileges: typing.Sequence[builtins.str],
    to_share: builtins.str,
    id: typing.Optional[builtins.str] = None,
    on_all_tables_in_schema: typing.Optional[builtins.str] = None,
    on_database: typing.Optional[builtins.str] = None,
    on_function: typing.Optional[builtins.str] = None,
    on_schema: typing.Optional[builtins.str] = None,
    on_table: typing.Optional[builtins.str] = None,
    on_tag: typing.Optional[builtins.str] = None,
    on_view: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GrantPrivilegesToShareTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59cea26894888819e5d3a518177002a860d0f6713cc39693e36bb5a1309c1cd9(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99cfe0f35561e2f0be61d97d9eb4e45509d099db3f1074af7a2d53ba5f63ad2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36ab90cdbadbdad3a61909f485ff63bb7f35baa6659210ac989a56643791b905(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__948b241207a85edab1eff75ff9db1649c6087e5f35a059840cac69057807dd10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32d073d15be8f6a890916b6ebea8c146491e54b72a42918ba3e915e35b1b0257(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c505c8350be84d542df63c04ea49b8ae5c26971a013cd695c7dcb576365e6050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e70d399249ba821daffb8ebbfc3b127051ade2a977597320d721340966a01494(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c9b6f75f28c7f8b4a02639cd7ef1d0631eb11321f390f8acb1f92a182d4961f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__807719716677fceabdf4f43f79140a3724b39b74a548c1eb9e43483885b242c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b04a967a791af1910930aa1cae37a53077bd98699d7eea09d42b5626fa6b7b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43b7a5a28d67aee81b8172f89f0b8cc74d713b0a87c786440962e1036195103(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5dc87562d29cd935055c6310cbf416df91caa02a79f0f39caa35c880965f49f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    privileges: typing.Sequence[builtins.str],
    to_share: builtins.str,
    id: typing.Optional[builtins.str] = None,
    on_all_tables_in_schema: typing.Optional[builtins.str] = None,
    on_database: typing.Optional[builtins.str] = None,
    on_function: typing.Optional[builtins.str] = None,
    on_schema: typing.Optional[builtins.str] = None,
    on_table: typing.Optional[builtins.str] = None,
    on_tag: typing.Optional[builtins.str] = None,
    on_view: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GrantPrivilegesToShareTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f0d63e40266bfe497e3f4a0bfb06d4ad83792ee513f729932dc6b29aea908be(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    read: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f41afdb8e8e1444fc8cda5292bf226cd850443d756a70ceffa55d6700b842f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__379a2ab8aa25135c928359aae45836bcf13abe8054aac6d9c013da4937add143(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab22b3fb153e18ee7ce4978ea9e60f2efcb5d677ad79d145382b9259cbb696d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__423440895de1f51c79e33cf3de78bca1fb7f98b969d596294d3d963f16a416ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f983329e880120661c9d1fbccd7a7af900d2ebffc93e9b9c9a34c4aea89068(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48df736c84c1fc335ef5b08ebbf512a263a20b6fa6c9f7378ce5373271fbe08d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GrantPrivilegesToShareTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
