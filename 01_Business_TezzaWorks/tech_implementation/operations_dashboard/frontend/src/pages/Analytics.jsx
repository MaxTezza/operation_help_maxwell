import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, DatePicker, Spin, message } from 'antd'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { ordersAPI } from '../utils/api'
import dayjs from 'dayjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const { RangePicker } = DatePicker

const Analytics = () => {
  const [loading, setLoading] = useState(true)
  const [analytics, setAnalytics] = useState(null)
  const [dateRange, setDateRange] = useState([
    dayjs().subtract(6, 'month'),
    dayjs()
  ])

  useEffect(() => {
    loadAnalytics()
  }, [dateRange])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const params = {
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD')
      }
      const response = await ordersAPI.getAnalytics(params)
      setAnalytics(response.data)
    } catch (error) {
      message.error('Failed to load analytics')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !analytics) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    )
  }

  // Monthly revenue chart data
  const monthlyRevenueData = {
    labels: analytics.monthly_revenue.map(m =>
      dayjs().month(m.month - 1).format('MMM YYYY')
    ),
    datasets: [
      {
        label: 'Revenue',
        data: analytics.monthly_revenue.map(m => m.revenue),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
      }
    ]
  }

  // Top products chart data
  const topProductsData = {
    labels: analytics.top_products.map(p => p.name),
    datasets: [
      {
        label: 'Revenue',
        data: analytics.top_products.map(p => p.revenue),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
        ]
      }
    ]
  }

  // Orders by status chart data
  const ordersByStatusData = {
    labels: Object.keys(analytics.orders_by_status).map(s =>
      s.replace('_', ' ').toUpperCase()
    ),
    datasets: [
      {
        data: Object.values(analytics.orders_by_status),
        backgroundColor: [
          'rgba(24, 144, 255, 0.8)',
          'rgba(19, 194, 194, 0.8)',
          'rgba(250, 140, 22, 0.8)',
          'rgba(82, 196, 26, 0.8)',
          'rgba(114, 46, 209, 0.8)',
        ]
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      }
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Analytics Dashboard</h1>
        <RangePicker
          value={dateRange}
          onChange={(dates) => setDateRange(dates)}
          format="MMM DD, YYYY"
        />
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Revenue"
              value={analytics.total_revenue}
              precision={2}
              prefix="$"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Orders"
              value={analytics.total_orders}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Average Order Value"
              value={analytics.average_order_value}
              precision={2}
              prefix="$"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Completed Orders"
              value={analytics.orders_by_status.delivered || 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Revenue Trend" className="chart-container">
            <div style={{ height: '300px' }}>
              <Line data={monthlyRevenueData} options={chartOptions} />
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Orders by Status" className="chart-container">
            <div style={{ height: '300px' }}>
              <Doughnut data={ordersByStatusData} options={chartOptions} />
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Top 5 Products by Revenue" className="chart-container">
            <div style={{ height: '300px' }}>
              <Bar data={topProductsData} options={chartOptions} />
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Revenue Breakdown by Status">
            <Row gutter={[16, 16]}>
              {Object.entries(analytics.revenue_by_status).map(([status, revenue]) => (
                <Col xs={24} sm={12} md={6} key={status}>
                  <div className="metric-card">
                    <div className="metric-label">
                      {status.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="metric-value">
                      ${revenue.toFixed(2)}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Analytics
