const ctx = document.getElementById("temp1h");
const ctx2 = document.getElementById("press1h");
const ctx3 = document.getElementById("hum1h");

fetch("/api/get1h")
  .then((response) => response.json())
  .then((data) => {
    createChart(data);
    //console.log(data);
  });

function createChart(data) {
  let date1 = data[3][8]+":"+data[3][9];
  let date2 = data[2][8]+":"+data[2][9];
  let date3 = data[1][8]+":"+data[1][9];
  let date4 = data[0][8]+":"+data[0][9];
  new Chart(ctx, {
    type: "line",
    data: {
      labels: [date1, date2, date3, date4],
      datasets: [
        {
          label: "Temperatura [°C]",
          data: [data[3][1], data[2][1], data[1][1], data[0][1]],
          borderWidth: 1,
          backgroundColor: "#466EFD",
          borderColor: "#466EFD",
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    },
  });
  new Chart(ctx2, {
    type: "line",
    data: {
      labels: [date1, date2, date3, date4],
      datasets: [
        {
          label: "Ciśnienie [hPa]",
          data: [data[3][2], data[2][2], data[1][2], data[0][2]],
          borderWidth: 1,
          backgroundColor: "#F6C109",
          borderColor: "#F6C109",
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    },
  });
  new Chart(ctx3, {
    type: "line",
    data: {
      labels: [date1, date2, date3, date4],
      datasets: [
        {
          label: "Wilgotność [%]",
          data: [data[3][3], data[2][3], data[1][3], data[0][3]],
          borderWidth: 1,
          backgroundColor: "#248754",
          borderColor: "#248754",
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    },
  });
}
