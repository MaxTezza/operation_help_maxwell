import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  InboxOutlined,
  BarChartOutlined,
  SettingOutlined
} from '@ant-design/icons'

// Pages
import Dashboard from './pages/Dashboard'
import Orders from './pages/Orders'
import OrderDetail from './pages/OrderDetail'
import CreateOrder from './pages/CreateOrder'
import Clients from './pages/Clients'
import ClientDetail from './pages/ClientDetail'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import KanbanBoard from './pages/KanbanBoard'
import Analytics from './pages/Analytics'

const { Header, Content, Sider } = Layout

function App() {
  const location = useLocation()

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/orders', icon: <ShoppingCartOutlined />, label: 'Orders' },
    { key: '/kanban', icon: <BarChartOutlined />, label: 'Production Board' },
    { key: '/clients', icon: <UserOutlined />, label: 'Clients' },
    { key: '/products', icon: <InboxOutlined />, label: 'Products' },
    { key: '/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        background: '#001529',
        padding: '0 24px'
      }}>
        <div className="logo" style={{
          color: 'white',
          fontSize: '20px',
          fontWeight: 'bold',
          marginRight: '40px'
        }}>
          TezzaWorks Dashboard
        </div>
      </Header>

      <Layout>
        <Sider width={200} theme="light">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderRight: 0 }}
          >
            {menuItems.map(item => (
              <Menu.Item key={item.key} icon={item.icon}>
                <Link to={item.key}>{item.label}</Link>
              </Menu.Item>
            ))}
          </Menu>
        </Sider>

        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              background: '#fff',
              padding: 24,
              margin: 0,
              minHeight: 280,
              borderRadius: '8px'
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/orders/new" element={<CreateOrder />} />
              <Route path="/orders/:id" element={<OrderDetail />} />
              <Route path="/kanban" element={<KanbanBoard />} />
              <Route path="/clients" element={<Clients />} />
              <Route path="/clients/:id" element={<ClientDetail />} />
              <Route path="/products" element={<Products />} />
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default App
