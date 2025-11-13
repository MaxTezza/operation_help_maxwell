module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setupTests.js'],
  moduleNameMapper: {
    '\.(css|less)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\.(js|jsx)$': 'babel-jest',
  },
  transformIgnorePatterns: [
    '/node_modules/(?!dnd-core|react-dnd|@react-dnd)',
  ],
  globals: {
    'import.meta': {
      env: {
        VITE_API_URL: 'http://localhost:5000/api',
      },
    },
  },
};