"use strict";
window.OPTIMIZATION_DEMO_DATA = {
  "schema_version": 1,
  "kind": "illustrative_computation_process",
  "economic_model_evaluated": false,
  "new_estimation_performed": false,
  "measured_benchmark": false,
  "units": "illustrative work units, not seconds",
  "parallel": {
    "jobs": [
      {
        "id": "A",
        "duration": 4
      },
      {
        "id": "B",
        "duration": 2
      },
      {
        "id": "C",
        "duration": 3
      },
      {
        "id": "D",
        "duration": 1
      },
      {
        "id": "E",
        "duration": 5
      },
      {
        "id": "F",
        "duration": 2
      },
      {
        "id": "G",
        "duration": 4
      },
      {
        "id": "H",
        "duration": 3
      }
    ],
    "axis_max": 27,
    "serial_prefix": 2,
    "serial_suffix": 1,
    "schedules": {
      "1": {
        "workers": 1,
        "events": [
          {
            "id": "A",
            "duration": 4,
            "worker": 0,
            "start": 0,
            "end": 4,
            "kind": "task"
          },
          {
            "id": "B",
            "duration": 2,
            "worker": 0,
            "start": 4,
            "end": 6,
            "kind": "task"
          },
          {
            "id": "C",
            "duration": 3,
            "worker": 0,
            "start": 6,
            "end": 9,
            "kind": "task"
          },
          {
            "id": "D",
            "duration": 1,
            "worker": 0,
            "start": 9,
            "end": 10,
            "kind": "task"
          },
          {
            "id": "E",
            "duration": 5,
            "worker": 0,
            "start": 10,
            "end": 15,
            "kind": "task"
          },
          {
            "id": "F",
            "duration": 2,
            "worker": 0,
            "start": 15,
            "end": 17,
            "kind": "task"
          },
          {
            "id": "G",
            "duration": 4,
            "worker": 0,
            "start": 17,
            "end": 21,
            "kind": "task"
          },
          {
            "id": "H",
            "duration": 3,
            "worker": 0,
            "start": 21,
            "end": 24,
            "kind": "task"
          }
        ],
        "makespan": 24,
        "speedup": 1.0,
        "total_with_serial": 27,
        "speedup_with_serial": 1.0,
        "makespan_label": "24 units",
        "speedup_label": "1.00\u00d7",
        "frames": [
          {
            "time": 0.0,
            "time_label": "0.00 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 0.25,
            "time_label": "0.25 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 0.5,
            "time_label": "0.50 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 0.75,
            "time_label": "0.75 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 1.0,
            "time_label": "1.00 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 1.25,
            "time_label": "1.25 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 1.5,
            "time_label": "1.50 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 1.75,
            "time_label": "1.75 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 2.0,
            "time_label": "2.00 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 2.25,
            "time_label": "2.25 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 2.5,
            "time_label": "2.50 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 2.75,
            "time_label": "2.75 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 3.0,
            "time_label": "3.00 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 3.25,
            "time_label": "3.25 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 3.5,
            "time_label": "3.50 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 3.75,
            "time_label": "3.75 units",
            "status": {
              "A": "running",
              "B": "queued",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 1,
            "queued": 7
          },
          {
            "time": 4.0,
            "time_label": "4.00 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 4.25,
            "time_label": "4.25 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 4.5,
            "time_label": "4.50 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 4.75,
            "time_label": "4.75 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 5.0,
            "time_label": "5.00 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 5.25,
            "time_label": "5.25 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 5.5,
            "time_label": "5.50 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 5.75,
            "time_label": "5.75 units",
            "status": {
              "A": "done",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 1,
            "queued": 6
          },
          {
            "time": 6.0,
            "time_label": "6.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 6.25,
            "time_label": "6.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 6.5,
            "time_label": "6.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 6.75,
            "time_label": "6.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 7.0,
            "time_label": "7.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 7.25,
            "time_label": "7.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 7.5,
            "time_label": "7.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 7.75,
            "time_label": "7.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 8.0,
            "time_label": "8.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 8.25,
            "time_label": "8.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 8.5,
            "time_label": "8.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 8.75,
            "time_label": "8.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 1,
            "queued": 5
          },
          {
            "time": 9.0,
            "time_label": "9.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 3,
            "running": 1,
            "queued": 4
          },
          {
            "time": 9.25,
            "time_label": "9.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 3,
            "running": 1,
            "queued": 4
          },
          {
            "time": 9.5,
            "time_label": "9.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 3,
            "running": 1,
            "queued": 4
          },
          {
            "time": 9.75,
            "time_label": "9.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 3,
            "running": 1,
            "queued": 4
          },
          {
            "time": 10.0,
            "time_label": "10.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 10.25,
            "time_label": "10.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 10.5,
            "time_label": "10.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 10.75,
            "time_label": "10.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 11.0,
            "time_label": "11.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 11.25,
            "time_label": "11.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 11.5,
            "time_label": "11.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 11.75,
            "time_label": "11.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 12.0,
            "time_label": "12.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 12.25,
            "time_label": "12.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 12.5,
            "time_label": "12.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 12.75,
            "time_label": "12.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 13.0,
            "time_label": "13.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 13.25,
            "time_label": "13.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 13.5,
            "time_label": "13.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 13.75,
            "time_label": "13.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 14.0,
            "time_label": "14.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 14.25,
            "time_label": "14.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 14.5,
            "time_label": "14.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 14.75,
            "time_label": "14.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 1,
            "queued": 3
          },
          {
            "time": 15.0,
            "time_label": "15.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 15.25,
            "time_label": "15.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 15.5,
            "time_label": "15.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 15.75,
            "time_label": "15.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 16.0,
            "time_label": "16.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 16.25,
            "time_label": "16.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 16.5,
            "time_label": "16.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 16.75,
            "time_label": "16.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 5,
            "running": 1,
            "queued": 2
          },
          {
            "time": 17.0,
            "time_label": "17.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 17.25,
            "time_label": "17.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 17.5,
            "time_label": "17.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 17.75,
            "time_label": "17.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 18.0,
            "time_label": "18.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 18.25,
            "time_label": "18.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 18.5,
            "time_label": "18.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 18.75,
            "time_label": "18.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 19.0,
            "time_label": "19.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 19.25,
            "time_label": "19.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 19.5,
            "time_label": "19.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 19.75,
            "time_label": "19.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 20.0,
            "time_label": "20.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 20.25,
            "time_label": "20.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 20.5,
            "time_label": "20.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 20.75,
            "time_label": "20.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 6,
            "running": 1,
            "queued": 1
          },
          {
            "time": 21.0,
            "time_label": "21.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 21.25,
            "time_label": "21.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 21.5,
            "time_label": "21.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 21.75,
            "time_label": "21.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 22.0,
            "time_label": "22.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 22.25,
            "time_label": "22.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 22.5,
            "time_label": "22.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 22.75,
            "time_label": "22.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 23.0,
            "time_label": "23.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 23.25,
            "time_label": "23.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 23.5,
            "time_label": "23.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 23.75,
            "time_label": "23.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 24.0,
            "time_label": "24.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.25,
            "time_label": "24.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.5,
            "time_label": "24.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.75,
            "time_label": "24.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.0,
            "time_label": "25.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.25,
            "time_label": "25.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.5,
            "time_label": "25.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.75,
            "time_label": "25.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.0,
            "time_label": "26.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.25,
            "time_label": "26.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.5,
            "time_label": "26.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.75,
            "time_label": "26.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 27.0,
            "time_label": "27.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          }
        ],
        "with_serial": {
          "events": [
            {
              "id": "Setup",
              "worker": 0,
              "start": 0,
              "end": 2,
              "duration": 2,
              "kind": "serial"
            },
            {
              "id": "A",
              "duration": 4,
              "worker": 0,
              "start": 2,
              "end": 6,
              "kind": "task"
            },
            {
              "id": "B",
              "duration": 2,
              "worker": 0,
              "start": 6,
              "end": 8,
              "kind": "task"
            },
            {
              "id": "C",
              "duration": 3,
              "worker": 0,
              "start": 8,
              "end": 11,
              "kind": "task"
            },
            {
              "id": "D",
              "duration": 1,
              "worker": 0,
              "start": 11,
              "end": 12,
              "kind": "task"
            },
            {
              "id": "E",
              "duration": 5,
              "worker": 0,
              "start": 12,
              "end": 17,
              "kind": "task"
            },
            {
              "id": "F",
              "duration": 2,
              "worker": 0,
              "start": 17,
              "end": 19,
              "kind": "task"
            },
            {
              "id": "G",
              "duration": 4,
              "worker": 0,
              "start": 19,
              "end": 23,
              "kind": "task"
            },
            {
              "id": "H",
              "duration": 3,
              "worker": 0,
              "start": 23,
              "end": 26,
              "kind": "task"
            },
            {
              "id": "Join",
              "worker": 0,
              "start": 26,
              "end": 27,
              "duration": 1,
              "kind": "serial"
            }
          ],
          "makespan": 27,
          "speedup": 1.0,
          "makespan_label": "27 units",
          "speedup_label": "1.00\u00d7",
          "frames": [
            {
              "time": 0.0,
              "time_label": "0.00 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.25,
              "time_label": "0.25 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.5,
              "time_label": "0.50 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.75,
              "time_label": "0.75 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.0,
              "time_label": "1.00 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.25,
              "time_label": "1.25 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.5,
              "time_label": "1.50 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.75,
              "time_label": "1.75 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 2.0,
              "time_label": "2.00 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 2.25,
              "time_label": "2.25 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 2.5,
              "time_label": "2.50 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 2.75,
              "time_label": "2.75 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 3.0,
              "time_label": "3.00 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 3.25,
              "time_label": "3.25 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 3.5,
              "time_label": "3.50 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 3.75,
              "time_label": "3.75 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 4.0,
              "time_label": "4.00 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 4.25,
              "time_label": "4.25 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 4.5,
              "time_label": "4.50 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 4.75,
              "time_label": "4.75 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 5.0,
              "time_label": "5.00 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 5.25,
              "time_label": "5.25 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 5.5,
              "time_label": "5.50 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 5.75,
              "time_label": "5.75 units",
              "status": {
                "A": "running",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 1,
              "queued": 7
            },
            {
              "time": 6.0,
              "time_label": "6.00 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 6.25,
              "time_label": "6.25 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 6.5,
              "time_label": "6.50 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 6.75,
              "time_label": "6.75 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 7.0,
              "time_label": "7.00 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 7.25,
              "time_label": "7.25 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 7.5,
              "time_label": "7.50 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 7.75,
              "time_label": "7.75 units",
              "status": {
                "A": "done",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 1,
              "queued": 6
            },
            {
              "time": 8.0,
              "time_label": "8.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 8.25,
              "time_label": "8.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 8.5,
              "time_label": "8.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 8.75,
              "time_label": "8.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 9.0,
              "time_label": "9.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 9.25,
              "time_label": "9.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 9.5,
              "time_label": "9.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 9.75,
              "time_label": "9.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 10.0,
              "time_label": "10.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 10.25,
              "time_label": "10.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 10.5,
              "time_label": "10.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 10.75,
              "time_label": "10.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 1,
              "queued": 5
            },
            {
              "time": 11.0,
              "time_label": "11.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 3,
              "running": 1,
              "queued": 4
            },
            {
              "time": 11.25,
              "time_label": "11.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 3,
              "running": 1,
              "queued": 4
            },
            {
              "time": 11.5,
              "time_label": "11.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 3,
              "running": 1,
              "queued": 4
            },
            {
              "time": 11.75,
              "time_label": "11.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 3,
              "running": 1,
              "queued": 4
            },
            {
              "time": 12.0,
              "time_label": "12.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 12.25,
              "time_label": "12.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 12.5,
              "time_label": "12.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 12.75,
              "time_label": "12.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 13.0,
              "time_label": "13.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 13.25,
              "time_label": "13.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 13.5,
              "time_label": "13.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 13.75,
              "time_label": "13.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 14.0,
              "time_label": "14.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 14.25,
              "time_label": "14.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 14.5,
              "time_label": "14.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 14.75,
              "time_label": "14.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 15.0,
              "time_label": "15.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 15.25,
              "time_label": "15.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 15.5,
              "time_label": "15.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 15.75,
              "time_label": "15.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 16.0,
              "time_label": "16.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 16.25,
              "time_label": "16.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 16.5,
              "time_label": "16.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 16.75,
              "time_label": "16.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 1,
              "queued": 3
            },
            {
              "time": 17.0,
              "time_label": "17.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 17.25,
              "time_label": "17.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 17.5,
              "time_label": "17.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 17.75,
              "time_label": "17.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 18.0,
              "time_label": "18.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 18.25,
              "time_label": "18.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 18.5,
              "time_label": "18.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 18.75,
              "time_label": "18.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 5,
              "running": 1,
              "queued": 2
            },
            {
              "time": 19.0,
              "time_label": "19.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 19.25,
              "time_label": "19.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 19.5,
              "time_label": "19.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 19.75,
              "time_label": "19.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 20.0,
              "time_label": "20.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 20.25,
              "time_label": "20.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 20.5,
              "time_label": "20.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 20.75,
              "time_label": "20.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 21.0,
              "time_label": "21.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 21.25,
              "time_label": "21.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 21.5,
              "time_label": "21.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 21.75,
              "time_label": "21.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 22.0,
              "time_label": "22.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 22.25,
              "time_label": "22.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 22.5,
              "time_label": "22.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 22.75,
              "time_label": "22.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 6,
              "running": 1,
              "queued": 1
            },
            {
              "time": 23.0,
              "time_label": "23.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 23.25,
              "time_label": "23.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 23.5,
              "time_label": "23.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 23.75,
              "time_label": "23.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 24.0,
              "time_label": "24.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 24.25,
              "time_label": "24.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 24.5,
              "time_label": "24.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 24.75,
              "time_label": "24.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 25.0,
              "time_label": "25.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 25.25,
              "time_label": "25.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 25.5,
              "time_label": "25.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 25.75,
              "time_label": "25.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 26.0,
              "time_label": "26.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.25,
              "time_label": "26.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.5,
              "time_label": "26.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.75,
              "time_label": "26.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 27.0,
              "time_label": "27.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            }
          ]
        }
      },
      "2": {
        "workers": 2,
        "events": [
          {
            "id": "A",
            "duration": 4,
            "worker": 0,
            "start": 0,
            "end": 4,
            "kind": "task"
          },
          {
            "id": "B",
            "duration": 2,
            "worker": 1,
            "start": 0,
            "end": 2,
            "kind": "task"
          },
          {
            "id": "C",
            "duration": 3,
            "worker": 1,
            "start": 2,
            "end": 5,
            "kind": "task"
          },
          {
            "id": "D",
            "duration": 1,
            "worker": 0,
            "start": 4,
            "end": 5,
            "kind": "task"
          },
          {
            "id": "E",
            "duration": 5,
            "worker": 0,
            "start": 5,
            "end": 10,
            "kind": "task"
          },
          {
            "id": "F",
            "duration": 2,
            "worker": 1,
            "start": 5,
            "end": 7,
            "kind": "task"
          },
          {
            "id": "G",
            "duration": 4,
            "worker": 1,
            "start": 7,
            "end": 11,
            "kind": "task"
          },
          {
            "id": "H",
            "duration": 3,
            "worker": 0,
            "start": 10,
            "end": 13,
            "kind": "task"
          }
        ],
        "makespan": 13,
        "speedup": 1.8461538461538463,
        "total_with_serial": 16,
        "speedup_with_serial": 1.6875,
        "makespan_label": "13 units",
        "speedup_label": "1.85\u00d7",
        "frames": [
          {
            "time": 0.0,
            "time_label": "0.00 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 0.25,
            "time_label": "0.25 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 0.5,
            "time_label": "0.50 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 0.75,
            "time_label": "0.75 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 1.0,
            "time_label": "1.00 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 1.25,
            "time_label": "1.25 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 1.5,
            "time_label": "1.50 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 1.75,
            "time_label": "1.75 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "queued",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 2,
            "queued": 6
          },
          {
            "time": 2.0,
            "time_label": "2.00 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 2.25,
            "time_label": "2.25 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 2.5,
            "time_label": "2.50 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 2.75,
            "time_label": "2.75 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 3.0,
            "time_label": "3.00 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 3.25,
            "time_label": "3.25 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 3.5,
            "time_label": "3.50 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 3.75,
            "time_label": "3.75 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "queued",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 2,
            "queued": 5
          },
          {
            "time": 4.0,
            "time_label": "4.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 2,
            "queued": 4
          },
          {
            "time": 4.25,
            "time_label": "4.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 2,
            "queued": 4
          },
          {
            "time": 4.5,
            "time_label": "4.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 2,
            "queued": 4
          },
          {
            "time": 4.75,
            "time_label": "4.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 2,
            "queued": 4
          },
          {
            "time": 5.0,
            "time_label": "5.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 5.25,
            "time_label": "5.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 5.5,
            "time_label": "5.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 5.75,
            "time_label": "5.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 6.0,
            "time_label": "6.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 6.25,
            "time_label": "6.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 6.5,
            "time_label": "6.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 6.75,
            "time_label": "6.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 4,
            "running": 2,
            "queued": 2
          },
          {
            "time": 7.0,
            "time_label": "7.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 7.25,
            "time_label": "7.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 7.5,
            "time_label": "7.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 7.75,
            "time_label": "7.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 8.0,
            "time_label": "8.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 8.25,
            "time_label": "8.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 8.5,
            "time_label": "8.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 8.75,
            "time_label": "8.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 9.0,
            "time_label": "9.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 9.25,
            "time_label": "9.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 9.5,
            "time_label": "9.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 9.75,
            "time_label": "9.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "queued"
            },
            "completed": 5,
            "running": 2,
            "queued": 1
          },
          {
            "time": 10.0,
            "time_label": "10.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 10.25,
            "time_label": "10.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 10.5,
            "time_label": "10.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 10.75,
            "time_label": "10.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 11.0,
            "time_label": "11.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 11.25,
            "time_label": "11.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 11.5,
            "time_label": "11.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 11.75,
            "time_label": "11.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 12.0,
            "time_label": "12.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 12.25,
            "time_label": "12.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 12.5,
            "time_label": "12.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 12.75,
            "time_label": "12.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "running"
            },
            "completed": 7,
            "running": 1,
            "queued": 0
          },
          {
            "time": 13.0,
            "time_label": "13.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.25,
            "time_label": "13.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.5,
            "time_label": "13.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.75,
            "time_label": "13.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.0,
            "time_label": "14.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.25,
            "time_label": "14.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.5,
            "time_label": "14.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.75,
            "time_label": "14.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.0,
            "time_label": "15.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.25,
            "time_label": "15.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.5,
            "time_label": "15.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.75,
            "time_label": "15.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.0,
            "time_label": "16.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.25,
            "time_label": "16.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.5,
            "time_label": "16.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.75,
            "time_label": "16.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.0,
            "time_label": "17.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.25,
            "time_label": "17.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.5,
            "time_label": "17.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.75,
            "time_label": "17.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.0,
            "time_label": "18.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.25,
            "time_label": "18.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.5,
            "time_label": "18.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.75,
            "time_label": "18.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.0,
            "time_label": "19.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.25,
            "time_label": "19.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.5,
            "time_label": "19.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.75,
            "time_label": "19.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.0,
            "time_label": "20.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.25,
            "time_label": "20.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.5,
            "time_label": "20.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.75,
            "time_label": "20.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.0,
            "time_label": "21.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.25,
            "time_label": "21.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.5,
            "time_label": "21.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.75,
            "time_label": "21.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.0,
            "time_label": "22.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.25,
            "time_label": "22.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.5,
            "time_label": "22.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.75,
            "time_label": "22.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.0,
            "time_label": "23.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.25,
            "time_label": "23.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.5,
            "time_label": "23.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.75,
            "time_label": "23.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.0,
            "time_label": "24.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.25,
            "time_label": "24.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.5,
            "time_label": "24.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.75,
            "time_label": "24.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.0,
            "time_label": "25.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.25,
            "time_label": "25.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.5,
            "time_label": "25.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.75,
            "time_label": "25.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.0,
            "time_label": "26.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.25,
            "time_label": "26.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.5,
            "time_label": "26.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.75,
            "time_label": "26.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 27.0,
            "time_label": "27.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          }
        ],
        "with_serial": {
          "events": [
            {
              "id": "Setup",
              "worker": 0,
              "start": 0,
              "end": 2,
              "duration": 2,
              "kind": "serial"
            },
            {
              "id": "A",
              "duration": 4,
              "worker": 0,
              "start": 2,
              "end": 6,
              "kind": "task"
            },
            {
              "id": "B",
              "duration": 2,
              "worker": 1,
              "start": 2,
              "end": 4,
              "kind": "task"
            },
            {
              "id": "C",
              "duration": 3,
              "worker": 1,
              "start": 4,
              "end": 7,
              "kind": "task"
            },
            {
              "id": "D",
              "duration": 1,
              "worker": 0,
              "start": 6,
              "end": 7,
              "kind": "task"
            },
            {
              "id": "E",
              "duration": 5,
              "worker": 0,
              "start": 7,
              "end": 12,
              "kind": "task"
            },
            {
              "id": "F",
              "duration": 2,
              "worker": 1,
              "start": 7,
              "end": 9,
              "kind": "task"
            },
            {
              "id": "G",
              "duration": 4,
              "worker": 1,
              "start": 9,
              "end": 13,
              "kind": "task"
            },
            {
              "id": "H",
              "duration": 3,
              "worker": 0,
              "start": 12,
              "end": 15,
              "kind": "task"
            },
            {
              "id": "Join",
              "worker": 0,
              "start": 15,
              "end": 16,
              "duration": 1,
              "kind": "serial"
            }
          ],
          "makespan": 16,
          "speedup": 1.6875,
          "makespan_label": "16 units",
          "speedup_label": "1.69\u00d7",
          "frames": [
            {
              "time": 0.0,
              "time_label": "0.00 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.25,
              "time_label": "0.25 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.5,
              "time_label": "0.50 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.75,
              "time_label": "0.75 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.0,
              "time_label": "1.00 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.25,
              "time_label": "1.25 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.5,
              "time_label": "1.50 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.75,
              "time_label": "1.75 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 2.0,
              "time_label": "2.00 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 2.25,
              "time_label": "2.25 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 2.5,
              "time_label": "2.50 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 2.75,
              "time_label": "2.75 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 3.0,
              "time_label": "3.00 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 3.25,
              "time_label": "3.25 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 3.5,
              "time_label": "3.50 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 3.75,
              "time_label": "3.75 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 2,
              "queued": 6
            },
            {
              "time": 4.0,
              "time_label": "4.00 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 4.25,
              "time_label": "4.25 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 4.5,
              "time_label": "4.50 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 4.75,
              "time_label": "4.75 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 5.0,
              "time_label": "5.00 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 5.25,
              "time_label": "5.25 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 5.5,
              "time_label": "5.50 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 5.75,
              "time_label": "5.75 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 2,
              "queued": 5
            },
            {
              "time": 6.0,
              "time_label": "6.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 2,
              "queued": 4
            },
            {
              "time": 6.25,
              "time_label": "6.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 2,
              "queued": 4
            },
            {
              "time": 6.5,
              "time_label": "6.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 2,
              "queued": 4
            },
            {
              "time": 6.75,
              "time_label": "6.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 2,
              "queued": 4
            },
            {
              "time": 7.0,
              "time_label": "7.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 7.25,
              "time_label": "7.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 7.5,
              "time_label": "7.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 7.75,
              "time_label": "7.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 8.0,
              "time_label": "8.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 8.25,
              "time_label": "8.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 8.5,
              "time_label": "8.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 8.75,
              "time_label": "8.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 4,
              "running": 2,
              "queued": 2
            },
            {
              "time": 9.0,
              "time_label": "9.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 9.25,
              "time_label": "9.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 9.5,
              "time_label": "9.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 9.75,
              "time_label": "9.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 10.0,
              "time_label": "10.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 10.25,
              "time_label": "10.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 10.5,
              "time_label": "10.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 10.75,
              "time_label": "10.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 11.0,
              "time_label": "11.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 11.25,
              "time_label": "11.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 11.5,
              "time_label": "11.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 11.75,
              "time_label": "11.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "queued"
              },
              "completed": 5,
              "running": 2,
              "queued": 1
            },
            {
              "time": 12.0,
              "time_label": "12.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 12.25,
              "time_label": "12.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 12.5,
              "time_label": "12.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 12.75,
              "time_label": "12.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 13.0,
              "time_label": "13.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 13.25,
              "time_label": "13.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 13.5,
              "time_label": "13.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 13.75,
              "time_label": "13.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 14.0,
              "time_label": "14.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 14.25,
              "time_label": "14.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 14.5,
              "time_label": "14.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 14.75,
              "time_label": "14.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "running"
              },
              "completed": 7,
              "running": 1,
              "queued": 0
            },
            {
              "time": 15.0,
              "time_label": "15.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.25,
              "time_label": "15.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.5,
              "time_label": "15.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.75,
              "time_label": "15.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.0,
              "time_label": "16.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.25,
              "time_label": "16.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.5,
              "time_label": "16.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.75,
              "time_label": "16.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.0,
              "time_label": "17.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.25,
              "time_label": "17.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.5,
              "time_label": "17.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.75,
              "time_label": "17.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.0,
              "time_label": "18.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.25,
              "time_label": "18.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.5,
              "time_label": "18.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.75,
              "time_label": "18.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.0,
              "time_label": "19.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.25,
              "time_label": "19.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.5,
              "time_label": "19.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.75,
              "time_label": "19.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.0,
              "time_label": "20.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.25,
              "time_label": "20.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.5,
              "time_label": "20.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.75,
              "time_label": "20.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.0,
              "time_label": "21.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.25,
              "time_label": "21.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.5,
              "time_label": "21.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.75,
              "time_label": "21.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.0,
              "time_label": "22.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.25,
              "time_label": "22.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.5,
              "time_label": "22.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.75,
              "time_label": "22.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.0,
              "time_label": "23.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.25,
              "time_label": "23.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.5,
              "time_label": "23.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.75,
              "time_label": "23.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.0,
              "time_label": "24.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.25,
              "time_label": "24.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.5,
              "time_label": "24.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.75,
              "time_label": "24.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.0,
              "time_label": "25.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.25,
              "time_label": "25.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.5,
              "time_label": "25.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.75,
              "time_label": "25.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.0,
              "time_label": "26.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.25,
              "time_label": "26.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.5,
              "time_label": "26.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.75,
              "time_label": "26.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 27.0,
              "time_label": "27.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            }
          ]
        }
      },
      "4": {
        "workers": 4,
        "events": [
          {
            "id": "A",
            "duration": 4,
            "worker": 0,
            "start": 0,
            "end": 4,
            "kind": "task"
          },
          {
            "id": "B",
            "duration": 2,
            "worker": 1,
            "start": 0,
            "end": 2,
            "kind": "task"
          },
          {
            "id": "C",
            "duration": 3,
            "worker": 2,
            "start": 0,
            "end": 3,
            "kind": "task"
          },
          {
            "id": "D",
            "duration": 1,
            "worker": 3,
            "start": 0,
            "end": 1,
            "kind": "task"
          },
          {
            "id": "E",
            "duration": 5,
            "worker": 3,
            "start": 1,
            "end": 6,
            "kind": "task"
          },
          {
            "id": "F",
            "duration": 2,
            "worker": 1,
            "start": 2,
            "end": 4,
            "kind": "task"
          },
          {
            "id": "G",
            "duration": 4,
            "worker": 2,
            "start": 3,
            "end": 7,
            "kind": "task"
          },
          {
            "id": "H",
            "duration": 3,
            "worker": 0,
            "start": 4,
            "end": 7,
            "kind": "task"
          }
        ],
        "makespan": 7,
        "speedup": 3.4285714285714284,
        "total_with_serial": 10,
        "speedup_with_serial": 2.7,
        "makespan_label": "7 units",
        "speedup_label": "3.43\u00d7",
        "frames": [
          {
            "time": 0.0,
            "time_label": "0.00 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 4,
            "queued": 4
          },
          {
            "time": 0.25,
            "time_label": "0.25 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 4,
            "queued": 4
          },
          {
            "time": 0.5,
            "time_label": "0.50 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 4,
            "queued": 4
          },
          {
            "time": 0.75,
            "time_label": "0.75 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "running",
              "E": "queued",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 0,
            "running": 4,
            "queued": 4
          },
          {
            "time": 1.0,
            "time_label": "1.00 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 4,
            "queued": 3
          },
          {
            "time": 1.25,
            "time_label": "1.25 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 4,
            "queued": 3
          },
          {
            "time": 1.5,
            "time_label": "1.50 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 4,
            "queued": 3
          },
          {
            "time": 1.75,
            "time_label": "1.75 units",
            "status": {
              "A": "running",
              "B": "running",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "queued",
              "G": "queued",
              "H": "queued"
            },
            "completed": 1,
            "running": 4,
            "queued": 3
          },
          {
            "time": 2.0,
            "time_label": "2.00 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 4,
            "queued": 2
          },
          {
            "time": 2.25,
            "time_label": "2.25 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 4,
            "queued": 2
          },
          {
            "time": 2.5,
            "time_label": "2.50 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 4,
            "queued": 2
          },
          {
            "time": 2.75,
            "time_label": "2.75 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "running",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "queued",
              "H": "queued"
            },
            "completed": 2,
            "running": 4,
            "queued": 2
          },
          {
            "time": 3.0,
            "time_label": "3.00 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "running",
              "H": "queued"
            },
            "completed": 3,
            "running": 4,
            "queued": 1
          },
          {
            "time": 3.25,
            "time_label": "3.25 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "running",
              "H": "queued"
            },
            "completed": 3,
            "running": 4,
            "queued": 1
          },
          {
            "time": 3.5,
            "time_label": "3.50 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "running",
              "H": "queued"
            },
            "completed": 3,
            "running": 4,
            "queued": 1
          },
          {
            "time": 3.75,
            "time_label": "3.75 units",
            "status": {
              "A": "running",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "running",
              "G": "running",
              "H": "queued"
            },
            "completed": 3,
            "running": 4,
            "queued": 1
          },
          {
            "time": 4.0,
            "time_label": "4.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 4.25,
            "time_label": "4.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 4.5,
            "time_label": "4.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 4.75,
            "time_label": "4.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 5.0,
            "time_label": "5.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 5.25,
            "time_label": "5.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 5.5,
            "time_label": "5.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 5.75,
            "time_label": "5.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "running",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 5,
            "running": 3,
            "queued": 0
          },
          {
            "time": 6.0,
            "time_label": "6.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 6.25,
            "time_label": "6.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 6.5,
            "time_label": "6.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 6.75,
            "time_label": "6.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "running",
              "H": "running"
            },
            "completed": 6,
            "running": 2,
            "queued": 0
          },
          {
            "time": 7.0,
            "time_label": "7.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 7.25,
            "time_label": "7.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 7.5,
            "time_label": "7.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 7.75,
            "time_label": "7.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 8.0,
            "time_label": "8.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 8.25,
            "time_label": "8.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 8.5,
            "time_label": "8.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 8.75,
            "time_label": "8.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 9.0,
            "time_label": "9.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 9.25,
            "time_label": "9.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 9.5,
            "time_label": "9.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 9.75,
            "time_label": "9.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 10.0,
            "time_label": "10.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 10.25,
            "time_label": "10.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 10.5,
            "time_label": "10.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 10.75,
            "time_label": "10.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 11.0,
            "time_label": "11.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 11.25,
            "time_label": "11.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 11.5,
            "time_label": "11.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 11.75,
            "time_label": "11.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 12.0,
            "time_label": "12.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 12.25,
            "time_label": "12.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 12.5,
            "time_label": "12.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 12.75,
            "time_label": "12.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.0,
            "time_label": "13.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.25,
            "time_label": "13.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.5,
            "time_label": "13.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 13.75,
            "time_label": "13.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.0,
            "time_label": "14.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.25,
            "time_label": "14.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.5,
            "time_label": "14.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 14.75,
            "time_label": "14.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.0,
            "time_label": "15.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.25,
            "time_label": "15.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.5,
            "time_label": "15.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 15.75,
            "time_label": "15.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.0,
            "time_label": "16.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.25,
            "time_label": "16.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.5,
            "time_label": "16.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 16.75,
            "time_label": "16.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.0,
            "time_label": "17.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.25,
            "time_label": "17.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.5,
            "time_label": "17.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 17.75,
            "time_label": "17.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.0,
            "time_label": "18.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.25,
            "time_label": "18.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.5,
            "time_label": "18.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 18.75,
            "time_label": "18.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.0,
            "time_label": "19.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.25,
            "time_label": "19.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.5,
            "time_label": "19.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 19.75,
            "time_label": "19.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.0,
            "time_label": "20.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.25,
            "time_label": "20.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.5,
            "time_label": "20.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 20.75,
            "time_label": "20.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.0,
            "time_label": "21.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.25,
            "time_label": "21.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.5,
            "time_label": "21.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 21.75,
            "time_label": "21.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.0,
            "time_label": "22.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.25,
            "time_label": "22.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.5,
            "time_label": "22.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 22.75,
            "time_label": "22.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.0,
            "time_label": "23.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.25,
            "time_label": "23.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.5,
            "time_label": "23.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 23.75,
            "time_label": "23.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.0,
            "time_label": "24.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.25,
            "time_label": "24.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.5,
            "time_label": "24.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 24.75,
            "time_label": "24.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.0,
            "time_label": "25.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.25,
            "time_label": "25.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.5,
            "time_label": "25.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 25.75,
            "time_label": "25.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.0,
            "time_label": "26.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.25,
            "time_label": "26.25 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.5,
            "time_label": "26.50 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 26.75,
            "time_label": "26.75 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          },
          {
            "time": 27.0,
            "time_label": "27.00 units",
            "status": {
              "A": "done",
              "B": "done",
              "C": "done",
              "D": "done",
              "E": "done",
              "F": "done",
              "G": "done",
              "H": "done"
            },
            "completed": 8,
            "running": 0,
            "queued": 0
          }
        ],
        "with_serial": {
          "events": [
            {
              "id": "Setup",
              "worker": 0,
              "start": 0,
              "end": 2,
              "duration": 2,
              "kind": "serial"
            },
            {
              "id": "A",
              "duration": 4,
              "worker": 0,
              "start": 2,
              "end": 6,
              "kind": "task"
            },
            {
              "id": "B",
              "duration": 2,
              "worker": 1,
              "start": 2,
              "end": 4,
              "kind": "task"
            },
            {
              "id": "C",
              "duration": 3,
              "worker": 2,
              "start": 2,
              "end": 5,
              "kind": "task"
            },
            {
              "id": "D",
              "duration": 1,
              "worker": 3,
              "start": 2,
              "end": 3,
              "kind": "task"
            },
            {
              "id": "E",
              "duration": 5,
              "worker": 3,
              "start": 3,
              "end": 8,
              "kind": "task"
            },
            {
              "id": "F",
              "duration": 2,
              "worker": 1,
              "start": 4,
              "end": 6,
              "kind": "task"
            },
            {
              "id": "G",
              "duration": 4,
              "worker": 2,
              "start": 5,
              "end": 9,
              "kind": "task"
            },
            {
              "id": "H",
              "duration": 3,
              "worker": 0,
              "start": 6,
              "end": 9,
              "kind": "task"
            },
            {
              "id": "Join",
              "worker": 0,
              "start": 9,
              "end": 10,
              "duration": 1,
              "kind": "serial"
            }
          ],
          "makespan": 10,
          "speedup": 2.7,
          "makespan_label": "10 units",
          "speedup_label": "2.70\u00d7",
          "frames": [
            {
              "time": 0.0,
              "time_label": "0.00 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.25,
              "time_label": "0.25 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.5,
              "time_label": "0.50 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 0.75,
              "time_label": "0.75 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.0,
              "time_label": "1.00 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.25,
              "time_label": "1.25 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.5,
              "time_label": "1.50 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 1.75,
              "time_label": "1.75 units",
              "status": {
                "A": "queued",
                "B": "queued",
                "C": "queued",
                "D": "queued",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 0,
              "queued": 8
            },
            {
              "time": 2.0,
              "time_label": "2.00 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 4,
              "queued": 4
            },
            {
              "time": 2.25,
              "time_label": "2.25 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 4,
              "queued": 4
            },
            {
              "time": 2.5,
              "time_label": "2.50 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 4,
              "queued": 4
            },
            {
              "time": 2.75,
              "time_label": "2.75 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "running",
                "E": "queued",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 0,
              "running": 4,
              "queued": 4
            },
            {
              "time": 3.0,
              "time_label": "3.00 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 4,
              "queued": 3
            },
            {
              "time": 3.25,
              "time_label": "3.25 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 4,
              "queued": 3
            },
            {
              "time": 3.5,
              "time_label": "3.50 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 4,
              "queued": 3
            },
            {
              "time": 3.75,
              "time_label": "3.75 units",
              "status": {
                "A": "running",
                "B": "running",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "queued",
                "G": "queued",
                "H": "queued"
              },
              "completed": 1,
              "running": 4,
              "queued": 3
            },
            {
              "time": 4.0,
              "time_label": "4.00 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 4,
              "queued": 2
            },
            {
              "time": 4.25,
              "time_label": "4.25 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 4,
              "queued": 2
            },
            {
              "time": 4.5,
              "time_label": "4.50 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 4,
              "queued": 2
            },
            {
              "time": 4.75,
              "time_label": "4.75 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "running",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "queued",
                "H": "queued"
              },
              "completed": 2,
              "running": 4,
              "queued": 2
            },
            {
              "time": 5.0,
              "time_label": "5.00 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "running",
                "H": "queued"
              },
              "completed": 3,
              "running": 4,
              "queued": 1
            },
            {
              "time": 5.25,
              "time_label": "5.25 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "running",
                "H": "queued"
              },
              "completed": 3,
              "running": 4,
              "queued": 1
            },
            {
              "time": 5.5,
              "time_label": "5.50 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "running",
                "H": "queued"
              },
              "completed": 3,
              "running": 4,
              "queued": 1
            },
            {
              "time": 5.75,
              "time_label": "5.75 units",
              "status": {
                "A": "running",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "running",
                "G": "running",
                "H": "queued"
              },
              "completed": 3,
              "running": 4,
              "queued": 1
            },
            {
              "time": 6.0,
              "time_label": "6.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 6.25,
              "time_label": "6.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 6.5,
              "time_label": "6.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 6.75,
              "time_label": "6.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 7.0,
              "time_label": "7.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 7.25,
              "time_label": "7.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 7.5,
              "time_label": "7.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 7.75,
              "time_label": "7.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "running",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 5,
              "running": 3,
              "queued": 0
            },
            {
              "time": 8.0,
              "time_label": "8.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 8.25,
              "time_label": "8.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 8.5,
              "time_label": "8.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 8.75,
              "time_label": "8.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "running",
                "H": "running"
              },
              "completed": 6,
              "running": 2,
              "queued": 0
            },
            {
              "time": 9.0,
              "time_label": "9.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 9.25,
              "time_label": "9.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 9.5,
              "time_label": "9.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 9.75,
              "time_label": "9.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 10.0,
              "time_label": "10.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 10.25,
              "time_label": "10.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 10.5,
              "time_label": "10.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 10.75,
              "time_label": "10.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 11.0,
              "time_label": "11.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 11.25,
              "time_label": "11.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 11.5,
              "time_label": "11.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 11.75,
              "time_label": "11.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 12.0,
              "time_label": "12.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 12.25,
              "time_label": "12.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 12.5,
              "time_label": "12.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 12.75,
              "time_label": "12.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 13.0,
              "time_label": "13.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 13.25,
              "time_label": "13.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 13.5,
              "time_label": "13.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 13.75,
              "time_label": "13.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 14.0,
              "time_label": "14.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 14.25,
              "time_label": "14.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 14.5,
              "time_label": "14.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 14.75,
              "time_label": "14.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.0,
              "time_label": "15.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.25,
              "time_label": "15.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.5,
              "time_label": "15.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 15.75,
              "time_label": "15.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.0,
              "time_label": "16.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.25,
              "time_label": "16.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.5,
              "time_label": "16.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 16.75,
              "time_label": "16.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.0,
              "time_label": "17.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.25,
              "time_label": "17.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.5,
              "time_label": "17.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 17.75,
              "time_label": "17.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.0,
              "time_label": "18.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.25,
              "time_label": "18.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.5,
              "time_label": "18.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 18.75,
              "time_label": "18.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.0,
              "time_label": "19.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.25,
              "time_label": "19.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.5,
              "time_label": "19.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 19.75,
              "time_label": "19.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.0,
              "time_label": "20.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.25,
              "time_label": "20.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.5,
              "time_label": "20.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 20.75,
              "time_label": "20.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.0,
              "time_label": "21.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.25,
              "time_label": "21.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.5,
              "time_label": "21.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 21.75,
              "time_label": "21.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.0,
              "time_label": "22.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.25,
              "time_label": "22.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.5,
              "time_label": "22.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 22.75,
              "time_label": "22.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.0,
              "time_label": "23.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.25,
              "time_label": "23.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.5,
              "time_label": "23.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 23.75,
              "time_label": "23.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.0,
              "time_label": "24.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.25,
              "time_label": "24.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.5,
              "time_label": "24.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 24.75,
              "time_label": "24.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.0,
              "time_label": "25.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.25,
              "time_label": "25.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.5,
              "time_label": "25.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 25.75,
              "time_label": "25.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.0,
              "time_label": "26.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.25,
              "time_label": "26.25 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.5,
              "time_label": "26.50 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 26.75,
              "time_label": "26.75 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            },
            {
              "time": 27.0,
              "time_label": "27.00 units",
              "status": {
                "A": "done",
                "B": "done",
                "C": "done",
                "D": "done",
                "E": "done",
                "F": "done",
                "G": "done",
                "H": "done"
              },
              "completed": 8,
              "running": 0,
              "queued": 0
            }
          ]
        }
      }
    }
  },
  "vectorization": {
    "weights": [
      [
        1,
        2,
        3,
        4
      ],
      [
        2,
        3,
        4,
        1
      ],
      [
        3,
        1,
        2,
        2
      ]
    ],
    "column_sums": [
      6,
      6,
      9,
      7
    ],
    "normalized": [
      [
        0.16666666666666666,
        0.3333333333333333,
        0.3333333333333333,
        0.5714285714285714
      ],
      [
        0.3333333333333333,
        0.5,
        0.4444444444444444,
        0.14285714285714285
      ],
      [
        0.5,
        0.16666666666666666,
        0.2222222222222222,
        0.2857142857142857
      ]
    ],
    "firms": 3,
    "markets": 4,
    "divisions": 12,
    "column_reductions": 4,
    "python_loop_passes": 4,
    "array_expressions": 1,
    "multicore_or_gpu_implied": false
  },
  "gpu_batch": {
    "batch_size": 4,
    "firms": 3,
    "markets": 4
  },
  "fusion": {
    "a": [
      1,
      -3,
      2,
      -2
    ],
    "b": [
      2,
      1,
      -5,
      4
    ],
    "x": [
      3,
      -2,
      -3,
      2
    ],
    "y": [
      6,
      -4,
      -6,
      4
    ],
    "z": [
      6,
      0,
      0,
      4
    ],
    "launches_before": 3,
    "launches_after": 1,
    "temporary_arrays_before": 2,
    "temporary_arrays_after": 0,
    "scope": "Small elementwise illustration; the actual share-update kernel also has per-market reductions."
  },
  "resident": {
    "stop_iterations": [
      2,
      4,
      3,
      5
    ],
    "max_iterations": 5,
    "launches_before": 5,
    "launches_after": 1,
    "scope": "Illustrative first-stop masks; no equilibrium residuals are simulated."
  }
};
