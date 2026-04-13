# frontend-design 技能

UI 逻辑封装技能，指导 AI 遵循企业样式规范与组件选型逻辑。

## 触发条件

- 前端组件开发
- UI 页面实现
- 样式规范调整

## 技术栈规范

### 组件库

| 组件类型 | 推荐组件 | 使用场景 |
|----------|----------|----------|
| 表单 | Form, Input, Select | 数据录入 |
| 表格 | Table, BaseTable | 数据展示 |
| 弹窗 | Modal, Drawer | 信息确认 |
| 导航 | Menu, Tabs | 页面导航 |
| 反馈 | Message, Notification | 操作反馈 |

### 样式规范

```css
/* 布局单位 */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;

/* 响应式断点 */
--breakpoint-sm: 576px;
--breakpoint-md: 768px;
--breakpoint-lg: 992px;
--breakpoint-xl: 1200px;

/* 主题色 */
--primary-color: #1890ff;
--success-color: #52c41a;
--warning-color: #faad14;
--error-color: #f5222d;
```

## 组件选型指南

### 1. 表单组件

```jsx
// 推荐写法
const MyForm = () => {
  const [form] = Form.useForm();
  
  return (
    <Form form={form} layout="vertical">
      <Form.Item name="field" label="字段" rules={[{ required: true }]}>
        <Input placeholder="请输入" />
      </Form.Item>
    </Form>
  );
};
```

### 2. 表格组件

```jsx
// 推荐写法
const MyTable = ({ data }) => {
  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '操作', key: 'action', render: (_, record) => <a>编辑</a> }
  ];
  
  return (
    <Table 
      columns={columns} 
      dataSource={data} 
      rowKey="id"
      pagination={{ pageSize: 10 }}
    />
  );
};
```

### 3. 消息提示

```jsx
// 推荐写法 - 使用 App.useApp()
const MyComponent = () => {
  const { message } = App.useApp();
  
  const handleSubmit = async () => {
    try {
      await saveData();
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };
};

// 禁止写法 - 静态方法
// message.success('成功'); // ✗ 会丢失上下文
```

## 响应式设计规范

### 布局原则

```css
/* 使用 Flexbox */
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.content {
  flex: 1;
  overflow: auto;
}

/* 使用视口单位 */
.header {
  height: 64px;
}

.sidebar {
  width: 240px;
  min-width: 200px;
}
```

### 媒体查询

```css
/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .content {
    padding: 8px;
  }
}
```

## 国际化规范

```jsx
// 使用 i18next
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('welcome')}</h1>
      <Button>{t('common.submit')}</Button>
    </div>
  );
};
```

## 相关技能

- [ui-ux-pro-max](./ui-ux-pro-max.md) - 交互优化
- [code-reviewer](./code-reviewer.md) - 代码审查
