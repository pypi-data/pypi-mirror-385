r'''
# Workflow Studio compatible State Machine

[![View on Construct Hub](https://constructs.dev/badge?package=%40matthewbonig%2Fstate-machine)](https://constructs.dev/packages/@matthewbonig/state-machine)

This is a Workflow Studio compatible AWS Step Function state machine construct.

The goal of this construct is to make it easy to build and maintain your state machines using the Workflow Studio but still
leverage the AWS CDK as the source of truth for the state machine.

Read more about it [here](https://matthewbonig.com/2022/02/19/step-functions-and-the-cdk/).

## How to Use This Construct

Start by designing your initial state machine using the Workflow Studio.
When done with your first draft, copy and paste the ASL definition to a local file.

Create a new instance of this construct, handing it a fully parsed version of the ASL.
Then add overridden values.
The fields in the `overrides` field should match the `States` field of the ASL.

## Version Usage

The AWS CDK `StateMachine` construct introduced a change in version [**2.85.0**](https://github.com/aws/aws-cdk/pull/25932) that deprecated an earlier usage of 'definition'
by this construct. This construct has been updated to use the new 'definitionBody' field.

If you are using a version of the CDK before version **2.85.0**, you should use version **0.0.28** of this construct.

If you are using a version fo the CDK great or equal to **2.85.0**, you should use version **0.0.29+** of this construct.

### Projen component

There is a projen component included in this library which will help you in using the construct. It works similar
to the [auto-discovery feature](https://projen.io/docs/integrations/aws/#aws-lambda-functions). To use it, first add the component
to your projen project:

```js
// ...
const { StepFunctionsAutoDiscover } = require('@matthewbonig/state-machine');

const project = new awscdk.AwsCdkTypeScriptApp({
  // ...,
  deps: [
    // ...,
    '@matthewbonig/state-machine',
  ]
});

new StepFunctionsAutoDiscover(project);
```

Now projen will look for any files with a suffix `.workflow.json` and generate new files beside the .json:

* A typed `overrides` interface which is based on your workflow.
* A construct derived from `StateMachine` that uses this override.

Instead of using the `StateMachine` construct directly you can now use the generated one:

```text
.
├── MyFancyThing.workflow.json
└── MyFancyThing-statemachine.ts
```

```python
export class SomeStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);
    const handler = new NodejsFunction(this, 'MyHandler');
    new SomeFancyThingStateMachine(this, 'MyFancyWorkflow', {
      overrides: {
        'My First State': {
          Parameters: {
            FunctionName: handler.functionName
          }
        }
      }
    })
  }
}
```

> :warning: **The interfaces and constructs generated here are NOT jsii compliant (they use Partials and Omits) and cannot be
> compiled by jsii into other languages. If you plan to distribute any libraries you cannot use this.**

### Alternative Extensions

There is an optional parameter, `extension` that you can pass to have it search for alternative extensions.
AWS recommends that ASL definition files have a `.asl.json` extension, which will be picked up by some IDE
tools. This extension was recommended after initial development of this component. Therefore, the default is
to use the original extension. But, you can override this by passing a different extension to the
AutoDiscover's constructor options. There are two constants defined, `JSON_STEPFUNCTION_EXT` and `AWS_RECOMMENDED_JSON_EXT` that you can use.

```js
// ...
const { StepFunctionsAutoDiscover, AWS_RECOMMENDED_JSON_EXT } = require('@matthewbonig/state-machine');

const project = new awscdk.AwsCdkTypeScriptApp({
  // ...,
  deps: [
    // ...,
    '@matthewbonig/state-machine',
  ]
});

new StepFunctionsAutoDiscover(project, { extension: AWS_RECOMMENDED_JSON_EXT });
```

### Yaml files

Yaml files are supported as well. You can provide an extension to the AutoDiscover component to have it search for yaml files. If the file has 'yaml' or 'yml' anywhere in the name it will be parsed as yaml. If not, it will be parsed as json.

```js
// ...
const { StepFunctionsAutoDiscover } = require('@matthewbonig/state-machine');

const project = new awscdk.AwsCdkTypeScriptApp({
  // ...,
  deps: [
    // ...,
    '@matthewbonig/state-machine',
  ]
});

new StepFunctionsAutoDiscover(project, { extension: '.yaml.asl' });
```

### Examples

```python
const secret = new Secret(stack, 'Secret', {});
new StateMachine(stack, 'Test', {
  stateMachineName: 'A nice state machine',
  definition: JSON.parse(fs.readFileSync(path.join(__dirname, 'sample.json'), 'utf8').toString()),
  overrides: {
    'Read database credentials secret': {
      Parameters: {
        SecretId: secret.secretArn,
      },
    },
  },
});
```

You can also override nested states in arrays, for example:

```python
new StateMachine(stack, 'Test', {
    stateMachineName: 'A-nice-state-machine',
    overrides: {
      Branches: [{
        // pass an empty object too offset overrides
      }, {
        StartAt: 'StartInstances',
        States: {
          StartInstances: {
            Parameters: {
              InstanceIds: ['INSTANCE_ID'],
            },
          },
        },
      }],
    },
    stateMachineType: StateMachineType.STANDARD,
    definition: {
      States: {
        Branches: [
          {
            StartAt: 'ResumeCluster',
            States: {
              'Redshift Pass': {
                Type: 'Pass',
                End: true,
              },
            },
          },
          {
            StartAt: 'StartInstances',
            States: {
              'StartInstances': {
                Type: 'Task',
                Parameters: {
                  InstanceIds: [
                    'MyData',
                  ],
                },
                Resource: 'arn:aws:states:::aws-sdk:ec2:startInstances',
                Next: 'DescribeInstanceStatus',
              },
              'DescribeInstanceStatus': {
                Type: 'Task',
                Next: 'EC2 Pass',
                Parameters: {
                  InstanceIds: [
                    'MyData',
                  ],
                },
                Resource: 'arn:aws:states:::aws-sdk:ec2:describeInstanceStatus',
              },
              'EC2 Pass': {
                Type: 'Pass',
                End: true,
              },
            },
          },
        ],
      },
    },
  });
```

For Python, be sure to use a context manager when opening your JSON file.

* You do not need to `str()` the dictionary object you supply as your `definition` prop.
* Elements of your override path **do** need to be strings.

```python
secret = Secret(stack, 'Secret')

with open('sample.json', 'r+', encoding='utf-8') as sample:
    sample_dict = json.load(sample)

state_machine = StateMachine(
    self,
    'Test',
    definition = sample_dict,
    overrides = {
    "Read database credentials secret": {
      "Parameters": {
        "SecretId": secret.secret_arn,
      },
    },
  })
```

In this example, the ASL has a state called 'Read database credentials secret' and the SecretId parameter is overridden with a
CDK generated value.
Future changes can be done by editing, debugging, and testing the state machine directly in the Workflow Studio.
Once everything is working properly, copy and paste the ASL back to your local file.

## Issues

Please open any issues you have on [Github](https://github.com/mbonig/state-machine/issues).

## Contributing

Please submit PRs from forked repositories if you'd like to contribute.
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import constructs as _constructs_77d1e7e8
import projen.awscdk as _projen_awscdk_04054675
import projen.cdk as _projen_cdk_04054675


class StateMachine(
    _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine,
    metaclass=jsii.JSIIMeta,
    jsii_type="@matthewbonig/state-machine.StateMachine",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        definition: typing.Any,
        asl_yaml: typing.Optional[builtins.bool] = None,
        logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        overrides: typing.Any = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param definition: An object that can be serialized into an ASL.
        :param asl_yaml: Should the ASL definition be written as YAML. Default: false
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param overrides: An object that matches the schema/shape of the ASL .States map with overridden values.
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__470c1f9840bf90327b7a15067476a056d8e6c623b9641c0bbdfcefd7ad0958e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateMachineProps(
            definition=definition,
            asl_yaml=asl_yaml,
            logs=logs,
            overrides=overrides,
            role=role,
            state_machine_name=state_machine_name,
            state_machine_type=state_machine_type,
            timeout=timeout,
            tracing_enabled=tracing_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@matthewbonig/state-machine.StateMachineProps",
    jsii_struct_bases=[],
    name_mapping={
        "definition": "definition",
        "asl_yaml": "aslYaml",
        "logs": "logs",
        "overrides": "overrides",
        "role": "role",
        "state_machine_name": "stateMachineName",
        "state_machine_type": "stateMachineType",
        "timeout": "timeout",
        "tracing_enabled": "tracingEnabled",
    },
)
class StateMachineProps:
    def __init__(
        self,
        *,
        definition: typing.Any,
        asl_yaml: typing.Optional[builtins.bool] = None,
        logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        overrides: typing.Any = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param definition: An object that can be serialized into an ASL.
        :param asl_yaml: Should the ASL definition be written as YAML. Default: false
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param overrides: An object that matches the schema/shape of the ASL .States map with overridden values.
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false
        '''
        if isinstance(logs, dict):
            logs = _aws_cdk_aws_stepfunctions_ceddda9d.LogOptions(**logs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83faeefbcd93a9a43e3a73870180709f3f441ca4082b11c441a11477932acce8)
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument asl_yaml", value=asl_yaml, expected_type=type_hints["asl_yaml"])
            check_type(argname="argument logs", value=logs, expected_type=type_hints["logs"])
            check_type(argname="argument overrides", value=overrides, expected_type=type_hints["overrides"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument state_machine_type", value=state_machine_type, expected_type=type_hints["state_machine_type"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument tracing_enabled", value=tracing_enabled, expected_type=type_hints["tracing_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "definition": definition,
        }
        if asl_yaml is not None:
            self._values["asl_yaml"] = asl_yaml
        if logs is not None:
            self._values["logs"] = logs
        if overrides is not None:
            self._values["overrides"] = overrides
        if role is not None:
            self._values["role"] = role
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if state_machine_type is not None:
            self._values["state_machine_type"] = state_machine_type
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing_enabled is not None:
            self._values["tracing_enabled"] = tracing_enabled

    @builtins.property
    def definition(self) -> typing.Any:
        '''An object that can be serialized into an ASL.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def asl_yaml(self) -> typing.Optional[builtins.bool]:
        '''Should the ASL definition be written as YAML.

        :default: false
        '''
        result = self._values.get("asl_yaml")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logs(self) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions]:
        '''Defines what execution history events are logged and where they are logged.

        :default: No logging
        '''
        result = self._values.get("logs")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions], result)

    @builtins.property
    def overrides(self) -> typing.Any:
        '''An object that matches the schema/shape of the ASL .States map with overridden values.

        Example::

            {'My First State': { Parameters: { FunctionName: 'aLambdaFunctionArn' } } }
        '''
        result = self._values.get("overrides")
        return typing.cast(typing.Any, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The execution role for the state machine service.

        :default: A role is automatically created
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''A name for the state machine.

        :default: A name is automatically generated
        '''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType]:
        '''Type of the state machine.

        :default: StateMachineType.STANDARD
        '''
        result = self._values.get("state_machine_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Maximum run time for this state machine.

        :default: No timeout
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def tracing_enabled(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether Amazon X-Ray tracing is enabled for this state machine.

        :default: false
        '''
        result = self._values.get("tracing_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateMachineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StepFunctionsAutoDiscover(
    _projen_cdk_04054675.AutoDiscoverBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@matthewbonig/state-machine.StepFunctionsAutoDiscover",
):
    '''A projen component for discovering AWS Step Function state machine workflow ASL files and generating a strongly typed interface and construct to use it.

    Simply add a new instance and hand it your AwsCdkTypeScriptApp projen class::

       const project = new AwsCdkTypeScriptApp({ ... });
       new StepFunctionsAutoDiscover(project);

    And any *.workflow.json file will cause the generation of a new strongly-typed StateMachine-derived class you can use.
    Note that these constructs are NOT jsii-compatible. If you need that,
    please open an `issue <https://github.com/mbonig/state-machine/issues/new>`_
    '''

    def __init__(
        self,
        project: _projen_awscdk_04054675.AwsCdkTypeScriptApp,
        *,
        extension: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param extension: An optional extension to use for discovering state machine files. Default: '.workflow.json' (JSON_STEPFUNCTION_EXT)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c649450e91e3d86f8bc8dcd15b8fc411dc8026258b00a2237b8e6584ba5a685f)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        _options = StepFunctionsAutoDiscoverOptions(extension=extension)

        jsii.create(self.__class__, self, [project, _options])


@jsii.data_type(
    jsii_type="@matthewbonig/state-machine.StepFunctionsAutoDiscoverOptions",
    jsii_struct_bases=[],
    name_mapping={"extension": "extension"},
)
class StepFunctionsAutoDiscoverOptions:
    def __init__(self, *, extension: typing.Optional[builtins.str] = None) -> None:
        '''
        :param extension: An optional extension to use for discovering state machine files. Default: '.workflow.json' (JSON_STEPFUNCTION_EXT)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4f1d2b9a4db46b698e396f194da56d74c782e43b0713389383441bd9dcf9ce3)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if extension is not None:
            self._values["extension"] = extension

    @builtins.property
    def extension(self) -> typing.Optional[builtins.str]:
        '''An optional extension to use for discovering state machine files.

        :default: '.workflow.json' (JSON_STEPFUNCTION_EXT)
        '''
        result = self._values.get("extension")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StepFunctionsAutoDiscoverOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "StateMachine",
    "StateMachineProps",
    "StepFunctionsAutoDiscover",
    "StepFunctionsAutoDiscoverOptions",
]

publication.publish()

def _typecheckingstub__470c1f9840bf90327b7a15067476a056d8e6c623b9641c0bbdfcefd7ad0958e3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    definition: typing.Any,
    asl_yaml: typing.Optional[builtins.bool] = None,
    logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    overrides: typing.Any = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    tracing_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83faeefbcd93a9a43e3a73870180709f3f441ca4082b11c441a11477932acce8(
    *,
    definition: typing.Any,
    asl_yaml: typing.Optional[builtins.bool] = None,
    logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    overrides: typing.Any = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    tracing_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c649450e91e3d86f8bc8dcd15b8fc411dc8026258b00a2237b8e6584ba5a685f(
    project: _projen_awscdk_04054675.AwsCdkTypeScriptApp,
    *,
    extension: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f1d2b9a4db46b698e396f194da56d74c782e43b0713389383441bd9dcf9ce3(
    *,
    extension: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
