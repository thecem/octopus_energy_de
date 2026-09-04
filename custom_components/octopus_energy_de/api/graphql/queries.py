"""GraphQL operations used by Octopus Energy DE."""

TOKEN_MUTATION = """
mutation krakenTokenAuthentication($email: String!, $password: String!) {
  obtainKrakenToken(input: { email: $email, password: $password }) {
    token
    payload
  }
}
"""

ACCOUNT_DISCOVERY_QUERY = """
query AccountDiscovery {
  viewer {
    accounts {
      number
      ledgers {
        balance
        ledgerType
      }
    }
  }
}
"""

TARIFF_QUERY = """
query Tariffs($accountNumber: String!) {
  account(accountNumber: $accountNumber) {
    id
    allProperties {
      id
      electricityMalos {
        maloNumber
        agreements {
          product {
            code
            description
            fullName
            isTimeOfUse
          }
          unitRateInformation {
            ... on SimpleProductUnitRateInformation {
              __typename
              latestGrossUnitRateCentsPerKwh
              grossRateInformation {
                date
                grossRate
                rateValidToDate
                vatRate
              }
            }
            ... on TimeOfUseProductUnitRateInformation {
              __typename
              rates {
                latestGrossUnitRateCentsPerKwh
                timeslotName
                timeslotActivationRules {
                  activeFromTime
                  activeToTime
                }
              }
            }
          }
          unitRateForecast {
            validFrom
            validTo
            unitRateInformation {
              __typename
              ... on SimpleProductUnitRateInformation {
                latestGrossUnitRateCentsPerKwh
              }
              ... on TimeOfUseProductUnitRateInformation {
                rates {
                  latestGrossUnitRateCentsPerKwh
                  timeslotName
                }
              }
            }
          }
          validFrom
          validTo
        }
      }
    }
  }
}
"""
