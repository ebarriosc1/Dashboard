
window.dash_clientside = Object.assign({}, window.dash_clientside, {

    apexCharts: {

        apexBar: function (Data,zipCodeColumns, selectedCountry) {

            // here we delete chart before redrawing 
            // comment the bellow line and see what happens
            console.log(zipCodeColumns)
            // data = tradeData.filter(item=>  item.country==='USA')
            var options = {
                series: [
                    {
                        name: 'ZipCode',
                        type: 'column',
                        data: Data
                    }
                 
                ],
                plotOptions:{
                    bar:{
                        horizontal:false,
                        columnWidth:'5px'
                    }
                },
                labels: zipCodeColumns,
                xaxis: { type: 'zipcode'},
                yaxis: [
                    { 
                        labels: { formatter:  BillionFormatter},
                        title: { text: "Counts "},
                    },
                ],
                fill: {
                    opacity: [0.85, 0.25, 1],
                    gradient: {
                        inverseColors: false,
                        shade: 'light',
                        type: "vertical",
                        opacityFrom: 0.85,
                        opacityTo: 0.55,
                        stops: [0, 100, 100, 100]
                    }
                },
                chart: { 
                    height: '100%',
                    width:'100%',
                },
                grid : {
                    show:false,
                    borderColor: '#e0e0e0',
                    strokeDashArray:[2,2],
                    stroke: {
                        opacity:0.1
                    },
                    xaxis: {
                        lines:{
                            show:true
                        }
                    },
                    yaxis: {
                        lines: {
                            show:true
                        }
                    },
                    padding: {
                        bottom:20
                    }
                },
                stroke: { width: [0, 0],  curve: 'smooth'},
                title: {
                    text: "Zip Code Distribution",
                    align: 'center',
                    style: {
                        fontSize:  '15px',
                        fontWeight:  'bold',
                    },
                },
                dataLabels: {
                    enabled: true,
                    enabledOnSeries: [1],
                    formatter: GigatonneFormatter
                  },
              };
              var chart = new ApexCharts(document.getElementById('apex-bars'), options);


            chart.render();

        return window.dash_clientside.no_update
            },

        apexBar2: function (Data, columns) {
                // here we delete chart before redrawing
                // comment the bellow line and see what happens
                // data = tradeData.filter(item=>  item.country==='USA')
                var options = {
                    chart: {
                        type: 'pie',
                        height: '100%',
                    },
                    labels: columns,
                    series: Data,
                    dataLabels: {
                        enabled: false // Disabling data labels since they are not necessary for a pie chart
                    },
                    legend: {
                        labels: {
                            colors: '#FFFFFF', 
                             // Change text color of legend labels to white
                        }
                    }
                };
            
            
                var chart2 = new ApexCharts(document.getElementById('apex-bars2'), options);
                chart2.render();
            
            
                return window.dash_clientside.no_update;
            },
        apexBar3: function (data_x, data_y) {
                // here we delete chart before redrawing
                // comment the bellow line and see what happens
                // data = tradeData.filter(item=>  item.country==='USA')
                var seriesData = data_x.map(function(item, index){
                    return {
                        x:item,
                        y:data_y[index]
                    };
                });
                var options = {
                    series:[ {
                        name:"Normal Distribution",
                        data:seriesData
                    }],
                    chart :{
                        height:150,
                        type:"line"
                    },
                    yaxis: {
                        labels:{
                            show:false
                        },
                    },
                    xaxis:{
                        labels:{
                            show:false
                        }
                    },

                    grid:{
                        show:false
                    }
                };
            
            
                var chart3 = new ApexCharts(document.getElementById('apex-bars3'), options);
                chart3.render();
                return window.dash_clientside.no_update;
            },
            
            
    },

});