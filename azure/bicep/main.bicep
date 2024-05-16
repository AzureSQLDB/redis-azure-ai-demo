targetScope = 'subscription'

@description('Optional. Azure main location to which the resources are to be deployed -defaults to the location of the current deployment')
param location string = deployment().location

@description('Optional. The tags to be assigned to the created resources.')
param tags object = {}

var applicationName = 'azureaidemo'

var defaultTags = union({
  application: applicationName
}, tags)

var appResourceGroupName = 'rg-${applicationName}'
var sharedResourceGroupName = 'rg-shared-${applicationName}'

// Create resource groups
resource appResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: appResourceGroupName
  location: location
  tags: defaultTags
}

resource sharedResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: sharedResourceGroupName
  location: location
  tags: defaultTags
}

// Create shared resources
module shared './shared/shared.bicep' = {
  name: 'sharedresources-Deployment'
  scope: resourceGroup(sharedResourceGroup.name)
  params: {
    location: location
    applicationName: applicationName
    tags: defaultTags
  }
}

//Create SQL Resource
module sql 'sql.bicep' = {
  scope: resourceGroup(appResourceGroup.name)
  name: 'sql-Deployment'
  params: {
    location: location
    tags: tags
    applicationName: applicationName
  }
}

//Create Redis resource
module redis 'redis.bicep' = {
  scope: resourceGroup(appResourceGroup.name)
  name: 'redis-Deployment'
  params: {
    location: location
    tags: defaultTags
    keyVaultName: shared.outputs.keyVaultName
    applicationName: applicationName
  }
}

//Create Function Apps
module functionApps 'func.bicep' = {
  dependsOn: [
   sql
   redis 
  ]
  scope: resourceGroup(appResourceGroup.name)
  name: 'functionApps-Deployment'
  params: {
    location: location
    tags: tags
    applicationName: applicationName
    appiConnectionString: shared.outputs.appInsightsConnectionString
  }
}

output appResourceGroupName string = appResourceGroup.name
output sharedResourceGroupName string = sharedResourceGroup.name
