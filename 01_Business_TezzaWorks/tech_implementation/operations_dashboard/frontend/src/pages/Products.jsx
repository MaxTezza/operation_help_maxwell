import React, { useState, useEffect } from 'react'
import { Table, Button, Input, Tag, message, Modal, Form, InputNumber, Select, Switch } from 'antd'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { productsAPI } from '../utils/api'

const Products = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [products, setProducts] = useState([])
  const [filteredProducts, setFilteredProducts] = useState([])
  const [searchText, setSearchText] = useState('')
  const [modalVisible, setModalVisible] = useState(false)
  const [categories, setCategories] = useState([])
  const [form] = Form.useForm()

  useEffect(() => {
    loadProducts()
    loadCategories()
  }, [])

  useEffect(() => {
    const filtered = products.filter(product =>
      product.name?.toLowerCase().includes(searchText.toLowerCase()) ||
      product.sku?.toLowerCase().includes(searchText.toLowerCase())
    )
    setFilteredProducts(filtered)
  }, [searchText, products])

  const loadProducts = async () => {
    try {
      setLoading(true)
      const response = await productsAPI.getAll()
      setProducts(response.data)
    } catch (error) {
      message.error('Failed to load products')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await productsAPI.getCategories()
      setCategories(response.data)
    } catch (error) {
      console.error(error)
    }
  }

  const handleCreateProduct = async (values) => {
    try {
      await productsAPI.create(values)
      message.success('Product created successfully')
      setModalVisible(false)
      form.resetFields()
      loadProducts()
    } catch (error) {
      message.error('Failed to create product')
      console.error(error)
    }
  }

  const columns = [
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      width: 120
    },
    {
      title: 'Product Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <a onClick={() => navigate(`/products/${record.id}`)}>{text}</a>
      )
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (category) => (
        <Tag color="blue">{category?.replace('_', ' ').toUpperCase()}</Tag>
      )
    },
    {
      title: 'Base Cost',
      dataIndex: 'base_cost',
      key: 'base_cost',
      render: (cost) => `$${cost?.toFixed(2)}`
    },
    {
      title: 'Stock',
      dataIndex: 'stock_quantity',
      key: 'stock_quantity',
      render: (stock, record) => {
        const isLow = stock <= record.reorder_level
        return (
          <Tag color={isLow ? 'red' : 'green'}>
            {stock} {isLow && '(Low)'}
          </Tag>
        )
      }
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/products/${record.id}`)}
        >
          View Details
        </Button>
      )
    }
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Products</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          Add Product
        </Button>
      </div>

      <div className="filter-bar">
        <Input
          placeholder="Search products..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
        />
      </div>

      <Table
        columns={columns}
        dataSource={filteredProducts}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total ${total} products`
        }}
      />

      <Modal
        title="Add New Product"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateProduct}
          initialValues={{
            overhead_percentage: 30,
            labor_hours: 0,
            stock_quantity: 0,
            reorder_level: 10,
            is_active: true,
            allows_logo: true,
            allows_personalization: false,
            customization_cost: 0
          }}
        >
          <Form.Item
            name="sku"
            label="SKU"
            rules={[{ required: true, message: 'Please enter SKU' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="name"
            label="Product Name"
            rules={[{ required: true, message: 'Please enter product name' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true, message: 'Please select category' }]}
          >
            <Select>
              {categories.map(cat => (
                <Select.Option key={cat.value} value={cat.value}>
                  {cat.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="base_cost"
            label="Base Cost ($)"
            rules={[{ required: true, message: 'Please enter base cost' }]}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="labor_hours" label="Labor Hours per Unit">
            <InputNumber min={0} step={0.25} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="overhead_percentage" label="Overhead Percentage (%)">
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="stock_quantity" label="Initial Stock Quantity">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="reorder_level" label="Reorder Level">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="allows_logo" label="Allows Logo" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item name="allows_personalization" label="Allows Personalization" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item name="customization_cost" label="Customization Cost ($)">
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Products
