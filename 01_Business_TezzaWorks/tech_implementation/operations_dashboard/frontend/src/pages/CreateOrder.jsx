import React from 'react'
import { Card, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const CreateOrder = () => {
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
      <h1>Create New Order</h1>
      <Card>
        <p>Order creation form - Full implementation available in complete dashboard</p>
      </Card>
    </div>
  )
}

export default CreateOrder
