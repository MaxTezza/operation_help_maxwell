import React from 'react'
import { Card, Descriptions, Table, Tag, Timeline, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const OrderDetail = () => {
  const navigate = useNavigate()

  return (
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/orders')}
        style={{ marginBottom: 16 }}
      >
        Back to Orders
      </Button>
      <h1>Order Details</h1>
      <Card>
        <p>Order detail view - Full implementation available in complete dashboard</p>
      </Card>
    </div>
  )
}

export default OrderDetail
