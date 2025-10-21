const d=function(){var a={defaultValue:null,kind:"LocalArgument",name:"count"},n={defaultValue:null,kind:"LocalArgument",name:"cursor"},e={defaultValue:"",kind:"LocalArgument",name:"search"},r={alias:null,args:null,kind:"ScalarField",name:"colorBy",storageKey:null},s={alias:null,args:null,kind:"ScalarField",name:"colorPool",storageKey:null},l={alias:null,args:null,kind:"ScalarField",name:"colorscale",storageKey:null},i={alias:null,args:null,kind:"ScalarField",name:"multicolorKeypoints",storageKey:null},u={alias:null,args:null,kind:"ScalarField",name:"showSkeletons",storageKey:null},o={alias:"allDatasets",args:null,kind:"ScalarField",name:"estimatedDatasetCount",storageKey:null},t=[{kind:"Variable",name:"after",variableName:"cursor"},{kind:"Variable",name:"first",variableName:"count"},{kind:"Variable",name:"search",variableName:"search"}];return{fragment:{argumentDefinitions:[a,n,e],kind:"Fragment",metadata:null,name:"IndexPageQuery",selections:[{alias:null,args:null,concreteType:"AppConfig",kind:"LinkedField",name:"config",plural:!1,selections:[r,s,l,i,u],storageKey:null},o,{args:null,kind:"FragmentSpread",name:"NavFragment"},{args:null,kind:"FragmentSpread",name:"configFragment"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[e,a,n],kind:"Operation",name:"IndexPageQuery",selections:[{alias:null,args:null,concreteType:"AppConfig",kind:"LinkedField",name:"config",plural:!1,selections:[r,s,l,i,u,{alias:null,args:null,kind:"ScalarField",name:"disableFrameFiltering",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"gridZoom",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"enableQueryPerformance",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"defaultQueryPerformance",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"loopVideos",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"mediaFallback",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"maxQueryTime",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"notebookHeight",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"plugins",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"showConfidence",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"showIndex",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"showLabel",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"showTooltip",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"theme",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"timezone",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"useFrameNumber",storageKey:null}],storageKey:null},o,{alias:null,args:null,kind:"ScalarField",name:"context",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dev",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"doNotTrack",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"uid",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"version",storageKey:null},{alias:null,args:t,concreteType:"DatasetStrConnection",kind:"LinkedField",name:"datasets",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"total",storageKey:null},{alias:null,args:null,concreteType:"DatasetStrEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"Dataset",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"DatasetStrPageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:t,filters:["search"],handle:"connection",key:"DatasetsList_query_datasets",kind:"LinkedHandle",name:"datasets"},l]},params:{cacheID:"ab024a0668ecc3c075f2a72e465f4602",id:null,metadata:{},name:"IndexPageQuery",operationKind:"query",text:`query IndexPageQuery(
  $search: String = ""
  $count: Int
  $cursor: String
) {
  config {
    colorBy
    colorPool
    colorscale
    multicolorKeypoints
    showSkeletons
  }
  allDatasets: estimatedDatasetCount
  ...NavFragment
  ...configFragment
}

fragment Analytics on Query {
  context
  dev
  doNotTrack
  uid
  version
}

fragment NavDatasets on Query {
  datasets(search: $search, first: $count, after: $cursor) {
    total
    edges {
      cursor
      node {
        name
        id
        __typename
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}

fragment NavFragment on Query {
  ...Analytics
  ...NavDatasets
}

fragment configFragment on Query {
  config {
    colorBy
    colorPool
    colorscale
    disableFrameFiltering
    gridZoom
    enableQueryPerformance
    defaultQueryPerformance
    loopVideos
    mediaFallback
    maxQueryTime
    multicolorKeypoints
    notebookHeight
    plugins
    showConfidence
    showIndex
    showLabel
    showSkeletons
    showTooltip
    theme
    timezone
    useFrameNumber
  }
  colorscale
}
`}}}();d.hash="0e29568fa34b45baaa1d820d64dbe63f";export{d as default};
