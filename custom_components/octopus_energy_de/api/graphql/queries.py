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
        meters {
          id
          meterType
          number
        }
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

ELECTRICITY_METER_READINGS_QUERY = """
query ElectricityMeterReadings($accountNumber: String!, $meterId: ID!) {
  electricityMeterReadings(accountNumber: $accountNumber, meterId: $meterId, first: 100) {
    edges {
      node {
        value
        readAt
        registerObisCode
        registerType
      }
    }
  }
}
"""

ELECTRICITY_CONSUMPTION_QUERY = """
query ElectricityConsumption($accountNumber: String!, $propertyId: ID!, $date: Date!) {
  account(accountNumber: $accountNumber) {
    property(id: $propertyId) {
      measurements(
        utilityFilters: {
          electricityFilters: {
            readingFrequencyType: RAW_INTERVAL
            readingQuality: COMBINED
          }
        }
        startOn: $date
        first: 200
      ) {
        edges {
          node {
            ... on IntervalMeasurementType {
              startAt
              endAt
              unit
              value
            }
          }
        }
      }
    }
  }
}
"""

SMARTFLEX_QUERY = """
query SmartFlex($accountNumber: String!) {
  completedDispatches(accountNumber: $accountNumber) {
    deltaKwh
    start
    startDt
    end
    endDt
  }
  devices(accountNumber: $accountNumber) {
    id
    name
    deviceType
    provider
    status {
      currentState
      isSuspended
      ... on SmartFlexVehicleStatus {
        activePower { value }
        stateOfCharge { value }
      }
      ... on SmartFlexChargePointStatus {
        stateOfCharge { value }
      }
    }
    ... on SmartFlexVehicle {
      vehicleVariant { batterySize }
    }
    ... on SmartFlexVehicle {
      chargingSessions(first: 100) {
        edges { node {
          start
          end
          energyAdded { value }
          cost { amount }
          ... on SmartFlexChargingSession { type }
        }}
      }
    }
    ... on SmartFlexChargePoint {
      chargingSessions(first: 100) {
        edges { node {
          start
          end
          energyAdded { value }
          cost { amount }
          ... on SmartFlexChargingSession { type }
        }}
      }
    }
  }
}
"""
