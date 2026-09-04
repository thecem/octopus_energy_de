"""Account and tariff GraphQL operations."""

ACCOUNT_DISCOVERY_QUERY = """
query AccountDiscovery {
  viewer { accounts { number ledgers { balance ledgerType } } }
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
        meters { id meterType number }
        agreements {
          product { code description fullName isTimeOfUse }
          unitRateInformation {
            ... on SimpleProductUnitRateInformation {
              __typename latestGrossUnitRateCentsPerKwh
              grossRateInformation { date grossRate rateValidToDate vatRate }
            }
            ... on TimeOfUseProductUnitRateInformation {
              __typename
              rates { latestGrossUnitRateCentsPerKwh timeslotName timeslotActivationRules { activeFromTime activeToTime } }
            }
          }
          unitRateForecast {
            validFrom validTo
            unitRateInformation {
              __typename
              ... on SimpleProductUnitRateInformation { latestGrossUnitRateCentsPerKwh }
              ... on TimeOfUseProductUnitRateInformation { rates { latestGrossUnitRateCentsPerKwh timeslotName } }
            }
          }
          validFrom validTo
        }
      }
    }
  }
}
"""
