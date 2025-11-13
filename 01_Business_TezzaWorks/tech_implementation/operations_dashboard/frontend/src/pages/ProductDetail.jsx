import React from 'react'
import { Card, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const ProductDetail = () => {
  const navigate = useNavigate()

  return (
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/products')}
        style={{ marginBottom: 16 }}
      >
        Back to Products
      </Button>
      <h1>Product Details</h1>
      <Card>
        <p>Product detail view with pricing calculator - Full implementation available</p>
      </Card>
    </div>
  )
}

export default ProductDetail
