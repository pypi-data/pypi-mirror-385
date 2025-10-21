## Python Joule Tools
Joule is a low-code real-time stream processing engine.

Joule currently supports wide range of data sources (such as Kafka, MQTT, RabbitMQ, InfuxDB, Minio S3 etc), 
machine learning inference, custom analytics, event windows 

## Why Should I Use This?
When you need to deploy and manage use cases within the Joule processing environment.

## Features
- Deploy transports, streams and use cases.
- Inspect all deployed specifications for transports, streams and use cases.
- List all deployed transports, streams and use cases.
- Undeploy transports, streams and use cases.
- Use case management to pause and resume processing.

## Installation
```bash
$ pip install joulectl
```

## Using joulectl
The tool provides a number of commands to 
support the deployment and management of Joule use case configurations

### Setup tool
First create a configuration file
```bash
joulectl config create
```

Now update the Joule host which you would like to connect too.
The default is ```localhost:9080```
```bash
joulectl config update --host 192.168.86.48:9080
```

You are now ready to deploy and manage joule remotely.

## Commands
List of available commands

### deploy
Deploy command for transports, streams and use cases.

#### Subcommands
- ```stream```     Deploy a stream
- ```transport```  Deploy a transport
- ```usecase```    Deploy a use case

### list
List deployed transports, streams and use cases.

#### Subcommands
- ```transports``` List transport by provided type
- ```streams```   List registered streams
- ```usecases```  List use cases

### inspect
Display deployed specification for transports, streams and use caase.

#### Subcommands
- ```stream```     Get a stream specification
- ```transport```  Get a transport specification
- ```usecase```    Get a use case specification

### usecase
Management command for use cases.

#### Subcommands
- ```pause```   Pause use case processing
- ```resume```  Resume use case processing

### undeploy
Use case management command for transports, streams and use cases.

#### Subcommands
- ```stream```     Undeploy stream
- ```transport```  Undeploy transport by provided type
- ```usecase```    Undeploy use case

### config
Configure tool setting.

#### Subcommands
- ```create```  Create a new configuration file.
- ```show```    Show configuration setting.
- ```update```  Update configuration setting.

## Resources
- Discord Joule [server](https://discord.com/channels/1080521605786116196/1080521606247493724)
- User and developer [documentation](https://docs.fractalworks.io/joule) 
- Joule [website](https://getjoule.io) 

## License
Joule Tools are released under an MIT License.