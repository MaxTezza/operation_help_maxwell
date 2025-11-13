import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Space, Spin } from 'antd'
import {
  DollarOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  RiseOutlined,
  WarningOutlined
} from '@ant-design/icons'
import { Link } from 'react-router-dom'
import { ordersAPI, productsAPI, clientsAPI } from '../utils/api'

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalRevenue: 0,
    totalOrders: 0,
    totalClients: 0,
    avgOrderValue: 0
  })
  const [recentOrders, setRecentOrders] = useState([])
  const [lowStockProducts, setLowStockProducts] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Get analytics data
      const analyticsRes = await ordersAPI.getAnalytics()
      setStats({
        totalRevenue: analyticsRes.data.total_revenue,
        totalOrders: analyticsRes.data.total_orders,
        avgOrderValue: analyticsRes.data.average_order_value,
      })

      // Get recent orders
      const ordersRes = await ordersAPI.getAll()
      setRecentOrders(ordersRes.data.slice(0, 5))

      // Get low stock products
      const lowStockRes = await productsAPI.getLowStock()
      setLowStockProducts(lowStockRes.data)

      // Get client count
      const clientsRes = await clientsAPI.getAll()
      setStats(prev => ({ ...prev, totalClients: clientsRes.data.length }))

    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const orderColumns = [
    {
      title: 'Order Number',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (text, record) => <Link to={`/orders/${record.id}`}>{text}</Link>
    },
    {
      title: 'Client',
      dataIndex: 'client_name',
      key: 'client_name',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          quote: 'blue',
          confirmed: 'cyan',
          in_production: 'orange',
          shipped: 'green',
          delivered: 'success',
        }
        return <Tag color={colors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>
      }
    },
    {
      title: 'Total',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount) => `$${amount?.toFixed(2) || '0.00'}`
    }
  ]

  const productColumns = [
    {
      title: 'Product',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => <Link to={`/products/${record.id}`}>{text}</Link>
    },
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
    },
    {
      title: 'Stock',
      dataIndex: 'stock_quantity',
      key: 'stock_quantity',
      render: (stock, record) => (
        <Space>
          <WarningOutlined style={{ color: '#ff4d4f' }} />
          {stock} / {record.reorder_level}
        </Space>
      )
    }
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Dashboard</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Revenue"
              value={stats.totalRevenue}
              precision={2}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Orders"
              value={stats.totalOrders}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Clients"
              value={stats.totalClients}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Avg Order Value"
              value={stats.avgOrderValue}
              precision={2}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="Recent Orders" extra={<Link to="/orders">View All</Link>}>
            <Table
              columns={orderColumns}
              dataSource={recentOrders}
              rowKey="id"
              pagination={false}
            />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card
            title="Low Stock Alert"
            extra={<Link to="/products">View All</Link>}
          >
            {lowStockProducts.length > 0 ? (
              <Table
                columns={productColumns}
                dataSource={lowStockProducts}
                rowKey="id"
                pagination={false}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '20px' }}>
                All products are well stocked!
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
