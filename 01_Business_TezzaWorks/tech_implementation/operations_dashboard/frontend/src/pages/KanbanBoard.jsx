import React, { useState, useEffect } from 'react'
import { Card, Tag, message, Spin, Modal } from 'antd'
import { DollarOutlined, CalendarOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { ordersAPI } from '../utils/api'
import dayjs from 'dayjs'

const KanbanBoard = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [kanbanData, setKanbanData] = useState({
    quote: [],
    confirmed: [],
    in_production: [],
    shipped: []
  })

  useEffect(() => {
    loadKanbanData()
  }, [])

  const loadKanbanData = async () => {
    try {
      setLoading(true)
      const response = await ordersAPI.getKanban()
      setKanbanData(response.data)
    } catch (error) {
      message.error('Failed to load kanban board')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await ordersAPI.updateStatus(orderId, newStatus)
      message.success('Order status updated')
      loadKanbanData()
    } catch (error) {
      message.error('Failed to update order status')
      console.error(error)
    }
  }

  const KanbanColumn = ({ title, status, orders, color }) => (
    <div className="kanban-column" style={{ flex: 1 }}>
      <div
        className="kanban-column-header"
        style={{ borderColor: color, color: color }}
      >
        {title} ({orders.length})
      </div>
      <div style={{ maxHeight: '70vh', overflowY: 'auto' }}>
        {orders.map(order => (
          <Card
            key={order.id}
            className="kanban-card"
            size="small"
            hoverable
            onClick={() => navigate(`/orders/${order.id}`)}
          >
            <div style={{ fontWeight: 'bold', marginBottom: 8 }}>
              {order.order_number}
            </div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
              {order.client_name}
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: 8
            }}>
              <span style={{ fontWeight: 500, color: '#1890ff' }}>
                <DollarOutlined /> ${order.total_amount?.toFixed(2)}
              </span>
              {order.estimated_completion_date && status === 'in_production' && (
                <span style={{ fontSize: '11px', color: '#999' }}>
                  <CalendarOutlined /> {dayjs(order.estimated_completion_date).format('MMM DD')}
                </span>
              )}
            </div>
            {order.special_instructions && (
              <div style={{
                marginTop: 8,
                padding: '4px 8px',
                background: '#fff7e6',
                borderRadius: 4,
                fontSize: '11px'
              }}>
                Special: {order.special_instructions.substring(0, 50)}...
              </div>
            )}
          </Card>
        ))}
        {orders.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '40px 20px',
            color: '#999'
          }}>
            No orders in this stage
          </div>
        )}
      </div>
    </div>
  )

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Production Workflow Board</h1>

      <div className="kanban-board">
        <KanbanColumn
          title="Quote"
          status="quote"
          orders={kanbanData.quote}
          color="#1890ff"
        />
        <KanbanColumn
          title="Confirmed"
          status="confirmed"
          orders={kanbanData.confirmed}
          color="#13c2c2"
        />
        <KanbanColumn
          title="In Production"
          status="in_production"
          orders={kanbanData.in_production}
          color="#fa8c16"
        />
        <KanbanColumn
          title="Shipped"
          status="shipped"
          orders={kanbanData.shipped}
          color="#52c41a"
        />
      </div>
    </div>
  )
}

export default KanbanBoard
