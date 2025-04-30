// 饼图
const pieCtx = document.getElementById('pieChart').getContext('2d');
new Chart(pieCtx, {
  type: 'pie',
  data: {
    labels: ['Math', 'Science', 'Coding', 'Reading'],
    datasets: [{
      data: [25, 20, 30, 25],
      backgroundColor: ['#3ec6a6', '#36c', '#09f', '#88f']
    }]
  },
  options: {
    responsive: true
  }
});

// 柱状图
const barCtx = document.getElementById('barChart').getContext('2d');
new Chart(barCtx, {
  type: 'bar',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    datasets: [{
      label: 'Study Minutes',
      data: [30, 45, 20, 60, 35],
      backgroundColor: '#3ec6a6'
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false }
    }
  }
});
