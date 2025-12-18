import React, { useMemo } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'
import { format } from 'date-fns'
import './WeatherChart.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

function WeatherChart({ location, weatherData, loading, onRefresh, searchDateRange = { startDate: null, endDate: null } }) {
  // Detect theme - use state to react to theme changes
  const [isDarkMode, setIsDarkMode] = React.useState(() => 
    document.documentElement.getAttribute('data-theme') === 'dark'
  )
  
  // View mode: 'overview' (days only) or 'day' (specific day with hours)
  const [viewMode, setViewMode] = React.useState('overview')
  const [selectedDay, setSelectedDay] = React.useState(null)
  
  React.useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDarkMode(document.documentElement.getAttribute('data-theme') === 'dark')
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    return () => observer.disconnect()
  }, [])
  
  const textColor = isDarkMode ? '#f1f5f9' : '#1a1a1a'
  const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
  
  // Group data by day
  const dataByDay = useMemo(() => {
    if (!weatherData || weatherData.length === 0) return {}
    
    const grouped = {}
    weatherData.forEach(reading => {
      const date = new Date(reading.timestamp)
      const dayKey = format(date, 'yyyy-MM-dd')
      const dayLabel = format(date, 'dd.MM.yyyy')
      
      if (!grouped[dayKey]) {
        grouped[dayKey] = {
          label: dayLabel,
          date: dayKey,
          readings: []
        }
      }
      grouped[dayKey].readings.push(reading)
    })
    
    // Sort readings within each day
    Object.values(grouped).forEach(day => {
      day.readings.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    })
    
    return grouped
  }, [weatherData])
  
  // Get days list for overview (filtered by search date range if provided)
  const daysList = useMemo(() => {
    let days = Object.values(dataByDay)
    
    // Filter by date range if search was performed
    if (searchDateRange.startDate || searchDateRange.endDate) {
      const start = searchDateRange.startDate ? new Date(searchDateRange.startDate).setHours(0, 0, 0, 0) : null
      const end = searchDateRange.endDate ? new Date(searchDateRange.endDate).setHours(23, 59, 59, 999) : null
      
      days = days.filter(day => {
        const dayDate = new Date(day.date).getTime()
        if (start && dayDate < start) return false
        if (end && dayDate > end) return false
        return true
      })
    }
    
    return days.sort((a, b) => a.date.localeCompare(b.date))
  }, [dataByDay, searchDateRange])

  const chartData = useMemo(() => {
    let displayData = []
    if (viewMode === 'day' && selectedDay) {
      displayData = dataByDay[selectedDay]?.readings || []
    } else {
      displayData = Object.values(dataByDay).map(day => {
        const latest = day.readings[day.readings.length - 1]
        return {
          ...latest,
          timestamp: day.date + 'T12:00:00',
          dayLabel: day.label
        }
      })
    }
    
    if (!displayData || displayData.length === 0) {
      return null
    }

    const sortedData = [...displayData].sort(
      (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
    )

    // Labels: show only day in overview, show time in day view
    const labels = sortedData.map((reading) => {
      if (viewMode === 'day') {
        return format(new Date(reading.timestamp), 'HH:mm')
      } else {
        return reading.dayLabel || format(new Date(reading.timestamp), 'dd.MM.yyyy')
      }
    })

    return {
      labels,
      datasets: [
        {
          label: 'Temperatur (°C)',
          data: sortedData.map((r) => r.temperature),
          borderColor: isDarkMode ? '#818cf8' : '#667eea',
          backgroundColor: isDarkMode ? 'rgba(129, 140, 248, 0.2)' : 'rgba(102, 126, 234, 0.2)',
          yAxisID: 'y',
          tension: 0.1,
        },
        {
          label: 'Luftfeuchtigkeit (%)',
          data: sortedData.map((r) => r.humidity),
          borderColor: isDarkMode ? '#a78bfa' : '#764ba2',
          backgroundColor: isDarkMode ? 'rgba(167, 139, 250, 0.2)' : 'rgba(118, 75, 162, 0.2)',
          yAxisID: 'y1',
          tension: 0.1,
        },
      ],
    }
  }, [weatherData, isDarkMode, viewMode, selectedDay, dataByDay])

  const precipitationData = useMemo(() => {
    let displayData = []
    if (viewMode === 'day' && selectedDay) {
      displayData = dataByDay[selectedDay]?.readings || []
    } else {
      displayData = Object.values(dataByDay).map(day => {
        const latest = day.readings[day.readings.length - 1]
        return {
          ...latest,
          timestamp: day.date + 'T12:00:00',
          dayLabel: day.label
        }
      })
    }
    
    if (!displayData || displayData.length === 0) {
      return null
    }

    const sortedData = [...displayData].sort(
      (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
    )

    // Labels: show only day in overview, show time in day view
    const labels = sortedData.map((reading) => {
      if (viewMode === 'day') {
        return format(new Date(reading.timestamp), 'HH:mm')
      } else {
        return reading.dayLabel || format(new Date(reading.timestamp), 'dd.MM.yyyy')
      }
    })

    return {
      labels,
      datasets: [
        {
          label: 'Niederschlag (mm)',
          data: sortedData.map((r) => r.precipitation),
          backgroundColor: isDarkMode ? 'rgba(129, 140, 248, 0.6)' : 'rgba(102, 126, 234, 0.6)',
        },
      ],
    }
  }, [weatherData, isDarkMode, viewMode, selectedDay, dataByDay])

  const options = useMemo(() => ({
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    onClick: (event, elements) => {
      if (viewMode === 'overview' && elements.length > 0) {
        // Get the clicked day
        const clickedIndex = elements[0].index
        const displayData = Object.values(dataByDay).map(day => {
          const latest = day.readings[day.readings.length - 1]
          return {
            ...latest,
            timestamp: day.date + 'T12:00:00',
            dayLabel: day.label
          }
        })
        const clickedReading = displayData[clickedIndex]
        if (clickedReading?.dayLabel) {
          // Find the day key
          const dayKey = Object.keys(dataByDay).find(key => 
            dataByDay[key].label === clickedReading.dayLabel
          )
          if (dayKey) {
            setSelectedDay(dayKey)
            setViewMode('day')
          }
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: textColor,
        },
      },
      title: {
        display: true,
        text: viewMode === 'day' 
          ? `Wetterdaten für ${location.name} - ${dataByDay[selectedDay]?.label || ''}`
          : `Wetterdaten für ${location.name} (Klicken Sie auf einen Tag für Details)`,
        color: textColor,
      },
      tooltip: {
        callbacks: {
          title: (items) => {
            if (viewMode === 'day') {
              return items[0].label + ' Uhr'
            } else {
              return items[0].label
            }
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColor,
        },
        grid: {
          color: gridColor,
        },
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Temperatur (°C)',
          color: textColor,
        },
        ticks: {
          color: textColor,
        },
        grid: {
          color: gridColor,
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Luftfeuchtigkeit (%)',
          color: textColor,
        },
        ticks: {
          color: textColor,
        },
        grid: {
          drawOnChartArea: false,
          color: gridColor,
        },
      },
    },
  }), [location.name, textColor, gridColor, viewMode, selectedDay, dataByDay])

  const barOptions = useMemo(() => ({
    responsive: true,
    onClick: (event, elements) => {
      if (viewMode === 'overview' && elements.length > 0) {
        // Get the clicked day
        const clickedIndex = elements[0].index
        const displayData = Object.values(dataByDay).map(day => {
          const latest = day.readings[day.readings.length - 1]
          return {
            ...latest,
            timestamp: day.date + 'T12:00:00',
            dayLabel: day.label
          }
        })
        const clickedReading = displayData[clickedIndex]
        if (clickedReading?.dayLabel) {
          // Find the day key
          const dayKey = Object.keys(dataByDay).find(key => 
            dataByDay[key].label === clickedReading.dayLabel
          )
          if (dayKey) {
            setSelectedDay(dayKey)
            setViewMode('day')
          }
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: textColor,
        },
      },
      title: {
        display: true,
        text: viewMode === 'day' 
          ? `Niederschlag - ${dataByDay[selectedDay]?.label || ''}`
          : 'Niederschlag (Klicken Sie auf einen Tag für Details)',
        color: textColor,
      },
      tooltip: {
        callbacks: {
          title: (items) => {
            if (viewMode === 'day') {
              return items[0].label + ' Uhr'
            } else {
              return items[0].label
            }
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColor,
        },
        grid: {
          color: gridColor,
        },
      },
      y: {
        beginAtZero: true,
        min: 0,
        max: (() => {
          const maxPrecip = Math.max(...(precipitationData?.datasets[0].data || [0]))
          // Wenn max 0 ist, zeige bis 1mm, damit die Balken sichtbar sind
          return maxPrecip === 0 ? 1 : Math.max(maxPrecip * 1.1, 1)
        })(),
        title: {
          display: true,
          text: 'Niederschlag (mm)',
          color: textColor,
        },
        ticks: {
          stepSize: 0.1,
          color: textColor,
        },
        grid: {
          color: gridColor,
        },
      },
    },
  }), [precipitationData, textColor, gridColor, viewMode, selectedDay, dataByDay])

  if (loading) {
    return (
      <div className="weather-chart">
        <div className="loading">Lade Wetterdaten...</div>
      </div>
    )
  }

  if (!weatherData || weatherData.length === 0) {
    return (
      <div className="weather-chart">
        <div className="chart-header">
          <h2>{location.name}</h2>
          <button className="refresh-btn" onClick={onRefresh} title="Aktualisieren">
            <span className="refresh-icon">🔄</span>
          </button>
        </div>
        <div className="no-data">Noch keine Wetterdaten verfügbar</div>
      </div>
    )
  }

  const latestReading = weatherData[0]
  const avgTemp = (
    weatherData.reduce((sum, r) => sum + r.temperature, 0) / weatherData.length
  ).toFixed(1)
  const avgHumidity = (
    weatherData.reduce((sum, r) => sum + r.humidity, 0) / weatherData.length
  ).toFixed(1)

  const handleBackToOverview = () => {
    setViewMode('overview')
    setSelectedDay(null)
  }

  // Format date range for display
  const formatDateRange = () => {
    if (!searchDateRange.startDate && !searchDateRange.endDate) {
      return null
    }
    const formatDate = (date) => {
      if (!date) return null
      return format(new Date(date), 'dd.MM.yyyy')
    }
    const start = formatDate(searchDateRange.startDate)
    const end = formatDate(searchDateRange.endDate)
    
    if (start && end) {
      return `${start} - ${end}`
    } else if (start) {
      return `Ab ${start}`
    } else if (end) {
      return `Bis ${end}`
    }
    return null
  }

  const dateRangeText = formatDateRange()

  return (
    <div className="weather-chart" data-view-mode={viewMode}>
      <div className="chart-header">
        <div className="chart-header-title">
          <h2>{location.name}</h2>
          {dateRangeText && (
            <div className="date-range-badge">
              📅 {dateRangeText}
            </div>
          )}
        </div>
        <div className="chart-header-actions">
          {viewMode === 'day' && (
            <button className="back-btn" onClick={handleBackToOverview} title="Zurück zur Übersicht">
              ← Übersicht
            </button>
          )}
          <button className="refresh-btn" onClick={onRefresh} title="Aktualisieren">
            <span className="refresh-icon">🔄</span>
          </button>
        </div>
      </div>
      
      {daysList.length > 0 && (
        <div className="days-list">
          {viewMode === 'overview' ? (
            <>
              <p className="days-list-hint">Klicken Sie auf einen Tag oder auf einen Punkt im Diagramm für Details:</p>
              <div className="days-grid">
                {daysList.map(day => (
                  <button
                    key={day.date}
                    className="day-button"
                    onClick={() => {
                      setSelectedDay(day.date)
                      setViewMode('day')
                    }}
                  >
                    {day.label}
                    <span className="day-count">({day.readings.length} Messungen)</span>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className="day-view-indicator">
                <span className="indicator-icon">📅</span>
                <span className="indicator-text">Tagesansicht: <strong>{dataByDay[selectedDay]?.label}</strong></span>
              </div>
              <div className="days-grid">
                {daysList.map(day => (
                  <button
                    key={day.date}
                    className={`day-button ${selectedDay === day.date ? 'day-button-active' : ''}`}
                    onClick={() => {
                      setSelectedDay(day.date)
                      setViewMode('day')
                    }}
                  >
                    {day.label}
                    <span className="day-count">({day.readings.length} Messungen)</span>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Aktuelle Temperatur</div>
          <div className="stat-value">{latestReading.temperature.toFixed(1)}°C</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Aktuelle Luftfeuchtigkeit</div>
          <div className="stat-value">{latestReading.humidity}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Durchschnittstemperatur</div>
          <div className="stat-value">{avgTemp}°C</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Durchschnittsluftfeuchtigkeit</div>
          <div className="stat-value">{avgHumidity}%</div>
        </div>
      </div>

      {chartData && (
        <div className="chart-container">
          <Line key={`line-${isDarkMode}`} data={chartData} options={options} />
        </div>
      )}

      {precipitationData && (
        <div className="chart-container">
          <Bar key={`bar-${isDarkMode}`} data={precipitationData} options={barOptions} />
          {precipitationData.datasets[0].data.every(v => v === 0 || v === null) && (
            <div className="no-precipitation-note">
              ⛈️ Kein Niederschlag in diesem Zeitraum gemessen
            </div>
          )}
        </div>
      )}

      <div className="data-count">
        {weatherData.length} Messungen angezeigt
      </div>
    </div>
  )
}

export default WeatherChart

