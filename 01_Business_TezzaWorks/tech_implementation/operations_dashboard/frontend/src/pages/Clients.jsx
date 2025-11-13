import React, { useState, useEffect } from 'react'
import { Table, Button, Input, Tag, Space, Modal, Form, message, Select } from 'antd'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { clientsAPI } from '../utils/api'

const Clients = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [clients, setClients] = useState([])
  const [filteredClients, setFilteredClients] = useState([])
  const [searchText, setSearchText] = useState('')
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadClients()
  }, [])

  useEffect(() => {
    const filtered = clients.filter(client =>
      client.company_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      client.contact_person?.toLowerCase().includes(searchText.toLowerCase()) ||
      client.email?.toLowerCase().includes(searchText.toLowerCase())
    )
    setFilteredClients(filtered)
  }, [searchText, clients])

  const loadClients = async () => {
    try {
      setLoading(true)
      const response = await clientsAPI.getAll()
      setClients(response.data)
    } catch (error) {
      message.error('Failed to load clients')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateClient = async (values) => {
    try {
      await clientsAPI.create(values)
      message.success('Client created successfully')
      setModalVisible(false)
      form.resetFields()
      loadClients()
    } catch (error) {
      message.error('Failed to create client')
      console.error(error)
    }
  }

  const columns = [
    {
      title: 'Company Name',
      dataIndex: 'company_name',
      key: 'company_name',
      render: (text, record) => (
        <a onClick={() => navigate(`/clients/${record.id}`)}>{text}</a>
      )
    },
    {
      title: 'Contact Person',
      dataIndex: 'contact_person',
      key: 'contact_person',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Phone',
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: 'Location',
      key: 'location',
      render: (_, record) => `${record.city || ''}, ${record.state || ''}`
    },
    {
      title: 'Source',
      dataIndex: 'acquisition_source',
      key: 'acquisition_source',
      render: (source) => (
        <Tag color="blue">
          {source?.replace('_', ' ').toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/clients/${record.id}`)}
        >
          View Details
        </Button>
      )
    }
  ]

  return (
    <div>
      <div className="page-header">
        <h1>Clients</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          Add Client
        </Button>
      </div>

      <div className="filter-bar">
        <Input
          placeholder="Search clients..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
        />
      </div>

      <Table
        columns={columns}
        dataSource={filteredClients}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total ${total} clients`
        }}
      />

      <Modal
        title="Add New Client"
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
          onFinish={handleCreateClient}
        >
          <Form.Item
            name="company_name"
            label="Company Name"
            rules={[{ required: true, message: 'Please enter company name' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="contact_person"
            label="Contact Person"
            rules={[{ required: true, message: 'Please enter contact person' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please enter email' },
              { type: 'email', message: 'Please enter a valid email' }
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item name="phone" label="Phone">
            <Input />
          </Form.Item>

          <Form.Item name="address" label="Address">
            <Input.TextArea rows={2} />
          </Form.Item>

          <Space style={{ width: '100%' }}>
            <Form.Item name="city" label="City" style={{ flex: 1 }}>
              <Input />
            </Form.Item>
            <Form.Item name="state" label="State" style={{ flex: 1 }}>
              <Input />
            </Form.Item>
            <Form.Item name="zip_code" label="ZIP" style={{ flex: 1 }}>
              <Input />
            </Form.Item>
          </Space>

          <Form.Item name="industry" label="Industry">
            <Input />
          </Form.Item>

          <Form.Item name="acquisition_source" label="How did they find us?">
            <Select>
              <Select.Option value="referral">Referral</Select.Option>
              <Select.Option value="website">Website</Select.Option>
              <Select.Option value="social_media">Social Media</Select.Option>
              <Select.Option value="trade_show">Trade Show</Select.Option>
              <Select.Option value="cold_outreach">Cold Outreach</Select.Option>
              <Select.Option value="existing_client">Existing Client</Select.Option>
              <Select.Option value="other">Other</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Clients
