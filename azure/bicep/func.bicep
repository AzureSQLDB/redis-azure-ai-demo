@description('Required. Main location')
param location string

@description('Optional. The tags to be assigned to the created resources.')
param tags object = {}

@description('Required. Application name')
param applicationName string

@description('The pricing tier for the hosting plan.')
@allowed([
  'D1'
  'F1'
  'B1'
  'B2'
  'B3'
  'S1'
  'S2'
  'S3'
  'P1'
  'P2'
  'P3'
  'P1V2'
  'P2V2'
  'P3V2'
  'I1'
  'I2'
  'I3'
  'Y1'
])
param sku string = 'S1'

@description('Optional. App Insights Connection String')
param appiConnectionString string = ''

@description('Optional. App Insights Instrumentation Key')
param appiInstrumentationKey string = ''

@description('Optional. Storage Account Name')
param storageAccountName string = ''

var resourceNames = {
  appServicePlanName: 'asp-${applicationName}-${location}-002'
  funcWriteBehindName: 'func-write-behind'
}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: resourceNames.appServicePlanName
  location: location
  tags:tags
  sku: {
    name: sku
  }
  kind: 'functionapp'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 0
    isSpot: false
    reserved: true
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
  }
}

resource funcWriteBehind 'Microsoft.Web/sites@2022-03-01' = {
  name: resourceNames.funcWriteBehindName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${resourceNames.funcWriteBehindName}.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${resourceNames.funcWriteBehindName}.scm.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: appServicePlan.id
    reserved: true
    isXenon: false
    hyperV: false
    vnetRouteAllEnabled: false
    vnetImagePullEnabled: false
    vnetContentShareEnabled: false
    siteConfig: {
      numberOfWorkers: 1
      linuxFxVersion: 'PYTHON|3.8'
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      http20Enabled: false
      functionAppScaleLimit: 200
      minimumElasticInstanceCount: 0
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    customDomainVerificationId: '863D812A4F8321ABD7EE56AC999CCEA38C9856F34D6BB6D836065FB757627DF1'
    containerSize: 1536
    dailyMemoryTimeQuota: 0
    httpsOnly: true
    redundancyMode: 'None'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
  }
}

// Get a reference to the existing storage
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

resource appsettings2 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: funcWriteBehind
  name: 'appsettings'
  properties: {
    AzureWebJobStorage: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${listKeys(storageAccount.id, '2021-09-01').keys[0].value}'
    APPINSIGHTS_INSTRUMENTATIONKEY: appiInstrumentationKey
    FUNCTIONS_EXTENSION_VERSION: '~4'
    ftpsState: 'Disabled'
    minTlsVersion: '1.2'
  }
}

output funcWriteBehindName string = funcWriteBehind.name
