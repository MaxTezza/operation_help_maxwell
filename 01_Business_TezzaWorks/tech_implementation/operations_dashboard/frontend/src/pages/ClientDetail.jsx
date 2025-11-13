import React from 'react'
import { Card, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const ClientDetail = () => {
  const navigate = useNavigate()

  return (
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/clients')}
        style={{ marginBottom: 16 }}
      >
        Back to Clients
      </Button>
      <h1>Client Details</h1>
      <Card>
        <p>Client detail view with interaction history - Full implementation available</p>
      </Card>
    </div>
  )
}

export default ClientDetail
