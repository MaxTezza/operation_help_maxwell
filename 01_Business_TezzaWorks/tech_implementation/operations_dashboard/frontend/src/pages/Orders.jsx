import React, { useState, useEffect } from 'react'
import { Table, Button, Tag, Space, Input, Select, DatePicker, message } from 'antd'
import { PlusOutlined, SearchOutlined, FilterOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { ordersAPI } from '../utils/api'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

const Orders = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [orders, setOrders] = useState([])
  const [filteredOrders, setFilteredOrders] = useState([])
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    dateRange: null
  })

  useEffect(() => {
    loadOrders()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [filters, orders])

  const loadOrders = async () => {
    try {
      setLoading(true)
      const response = await ordersAPI.getAll()
      setOrders(response.data)
    } catch (error) {
      message.error('Failed to load orders')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...orders]

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filtered = filtered.filter(order =>
        order.order_number?.toLowerCase().includes(searchLower) ||
        order.client_name?.toLowerCase().includes(searchLower)
      )
    }

    // Status filter
    if (filters.status) {
      filtered = filtered.filter(order => order.status === filters.status)
    }

    // Date range filter
    if (filters.dateRange && filters.dateRange.length === 2) {
      const [start, end] = filters.dateRange
      filtered = filtered.filter(order => {
        const orderDate = dayjs(order.order_date)
        return orderDate.isAfter(start) && orderDate.isBefore(end)
      })
    }

    setFilteredOrders(filtered)
  }

  const handleDeleteOrder = async (id) => {
    try {
      await ordersAPI.delete(id)
      message.success('Order deleted successfully')
      loadOrders()
    } catch (error) {
      message.error('Failed to delete order')
      console.error(error)
    }
  }

  const columns = [
    {
      title: 'Order Number',
      dataIndex: 'order_number',
      key: 'order_number',
      render: (text, record) => (
        <Link to={`/orders/${record.id}`} style={{ fontWeight: 500 }}>
          {text}
        </Link>
      )
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
          cancelled: 'red'
        }
        return (
          <Tag color={colors[status]}>
            {status.replace('_', ' ').toUpperCase()}
          </Tag>
        )
      }
    },
    {
      title: 'Order Date',
      dataIndex: 'order_date',
      key: 'order_date',
      render: (date) => date ? dayjs(date).format('MMM DD, YYYY') : '-'
    },
    {
      title: 'Total Amount',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount) => `$${amount?.toFixed(2) || '0.00'}`,
      sorter: (a, b) => a.total_amount - b.total_amount
    },
    {
      title: 'Profit Margin',
      dataIndex: 'profit_margin',
      key: 'profit_margin',
      render: (margin) => `${margin?.toFixed(1) || '0.0'}%`,
      sorter: (a, b) => a.profit_margin - b.profit_margin
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            onClick={() => navigate(`/orders/${record.id}`)}
          >
            View
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Orders</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/orders/new')}
        >
          Create Order
        </Button>
      </div>

      <div className="filter-bar">
        <Input
          placeholder="Search orders..."
          prefix={<SearchOutlined />}
          style={{ width: 250 }}
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          allowClear
        />

        <Select
          placeholder="Filter by status"
          style={{ width: 180 }}
          value={filters.status || undefined}
          onChange={(value) => setFilters({ ...filters, status: value })}
          allowClear
        >
          <Select.Option value="quote">Quote</Select.Option>
          <Select.Option value="confirmed">Confirmed</Select.Option>
          <Select.Option value="in_production">In Production</Select.Option>
          <Select.Option value="shipped">Shipped</Select.Option>
          <Select.Option value="delivered">Delivered</Select.Option>
        </Select>

        <RangePicker
          onChange={(dates) => setFilters({ ...filters, dateRange: dates })}
        />
      </div>

      <Table
        columns={columns}
        dataSource={filteredOrders}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total ${total} orders`
        }}
      />
    </div>
  )
}

export default Orders
