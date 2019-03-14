start_case_mutation = """\
mutation startCase($case: StartCaseInput!) {
  startCase(input: $case) {
    case {
      id
    }
  }
}\
"""

intervalled_forms_query = """\
query allInterForms {
  allForms (metaHasKey: "interval") {
    pageInfo {
      startCursor
      endCursor
    }
    edges {
      node {
        meta
        id
        slug
        documents {
          edges {
            node {
              case {
                closedAt
                closedByUser
                status
              }
            }
          }
        }
      }
    }
  }
}\
"""
