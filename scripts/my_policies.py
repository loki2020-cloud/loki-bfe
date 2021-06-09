devices_have_routes = {
  "description": "CE1 networks on CE2",
  "title": "CE2 - Received routes",
  "devices_have_routes": {
    "vrfs": {
      "devices": {
        "hostname": {
          "regex": "ce2"
        }
      },
      "name": {
        "regex": ".*"
      }
    },
    "routes": {
      "all": {
        "of": [
          {
            "network": {
              "equals": "100.1.0.1/32"
            },
            "bgp": {}
          },
          {
            "network": {
              "equals": "100.1.1.1/32"
            },
            "bgp": {}
          },
          {
            "network": {
              "equals": "100.1.2.1/32"
            },
            "bgp": {}
          },
          {
            "network": {
              "equals": "100.1.3.1/32"
            },
            "bgp": {}
          }
        ]
      }
    }
  }
}

filter_behavior_denied = {
  "description": "100.1.1.1 denied",
  "title": "ce2 to ce1",
  "filter_behavior": {
    "devices": {
      "hostname": {
        "regex": "pe3"
      }
    },
    "filters": {
      "name": {
        "regex": "100"
      }
    },
    "flows": {
      "include": [
        {
          "src_ips": [
            {
              "exact_match": "200.1.1.1"
            }
          ],
          "dst_ips": [
            {
              "exact_match": "100.1.1.1"
            }
          ],
          "apps": [
            "tcp"
          ]
        },
        {
          "src_ips": [
            {
              "exact_match": "200.1.1.1"
            }
          ],
          "dst_ips": [
            {
              "exact_match": "100.1.2.1"
            }
          ],
          "apps": [
            "tcp"
          ]
        }
      ]
    },
    "expect": {
      "action": "DENY"
    }
  }
}

filter_behavior_allowed = {
  "description": "allowed on ce1",
  "title": "ce2 permitted",
  "filter_behavior": {
    "devices": {
      "hostname": {
        "regex": "pe3"
      }
    },
    "filters": {
      "name": {
        "regex": "100"
      }
    },
    "flows": {
      "include": [
        {
          "src_ips": [
            {
              "exact_match": "200.1.1.1"
            }
          ],
          "dst_ips": [
            {
              "exact_match": "100.1.1.1"
            }
          ],
          "apps": [
            "tcp"
          ]
        }
      ]
    },
    "expect": {
      "action": "PERMIT"
    }
  }
}
