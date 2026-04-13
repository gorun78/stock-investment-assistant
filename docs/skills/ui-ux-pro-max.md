# ui-ux-pro-max 技能

交互体验优化技能，强化 UI 细节感知，提升 AI 对复杂交互实现的审美。

## 触发条件

- UI 交互优化任务
- 用户体验改进
- 前端组件细节完善

## 核心能力

### 1. 交互反馈优化

| 场景 | 优化方案 | 实现方式 |
|------|----------|----------|
| 按钮点击 | 加载状态 + 禁用 | `loading` + `disabled` |
| 表单提交 | 进度提示 | `Spin` + `message` |
| 数据加载 | 骨架屏 | `Skeleton` 组件 |
| 操作成功 | 成功提示 | `message.success()` |
| 操作失败 | 错误提示 + 重试 | `message.error()` + 重试按钮 |

### 2. 状态管理

```jsx
// 加载状态
const [loading, setLoading] = useState(false);

// 提交处理
const handleSubmit = async () => {
  setLoading(true);
  try {
    await saveData();
    message.success('保存成功');
  } catch (error) {
    message.error('保存失败: ' + error.message);
  } finally {
    setLoading(false);
  }
};

// 按钮状态
<Button type="primary" loading={loading} onClick={handleSubmit}>
  提交
</Button>
```

### 3. 表单体验优化

```jsx
// 实时验证
<Form.Item 
  name="email" 
  rules={[
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '邮箱格式不正确' }
  ]}
  validateTrigger="onBlur"
>
  <Input placeholder="请输入邮箱" />
</Form.Item>

// 密码强度提示
<Form.Item name="password" rules={[{ min: 8, message: '密码至少8位' }]}>
  <Input.Password placeholder="请输入密码" />
</Form.Item>
```

### 4. 列表体验优化

```jsx
// 空状态
<Table
  dataSource={data}
  columns={columns}
  locale={{
    emptyText: <Empty description="暂无数据" />
  }}
/>

// 加载更多
<List
  loadMore={
    <div style={{ textAlign: 'center', marginTop: 12 }}>
      <Button onClick={onLoadMore}>加载更多</Button>
    </div>
  }
/>

// 虚拟滚动
<List
  dataSource={largeData}
  renderItem={renderItem}
  pagination={{ pageSize: 20 }}
/>
```

### 5. 错误边界

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <Result status="error" title="出错了" extra={<Button onClick={() => location.reload()}>刷新页面</Button>} />;
    }
    return this.props.children;
  }
}
```

## 交互模式库

### 确认类交互

```jsx
// 删除确认
const handleDelete = () => {
  Modal.confirm({
    title: '确认删除',
    content: '删除后数据将无法恢复，确定要删除吗？',
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      await deleteItem();
      message.success('删除成功');
    }
  });
};
```

### 批量操作

```jsx
// 批量选择
const [selectedKeys, setSelectedKeys] = useState([]);

<Table
  rowSelection={{
    selectedRowKeys: selectedKeys,
    onChange: setSelectedKeys
  }}
/>

// 批量操作栏
{selectedKeys.length > 0 && (
  <Affix offsetBottom={20}>
    <Card>
      已选择 {selectedKeys.length} 项
      <Button danger onClick={handleBatchDelete}>批量删除</Button>
    </Card>
  </Affix>
)}
```

### 拖拽排序

```jsx
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';

<DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
  <SortableContext items={items} strategy={verticalListSortingStrategy}>
    {items.map(item => <SortableItem key={item.id} item={item} />)}
  </SortableContext>
</DndContext>
```

## 响应式设计

### 断点适配

```css
/* 移动端 */
@media (max-width: 576px) {
  .container { padding: 8px; }
  .sidebar { display: none; }
}

/* 平板 */
@media (min-width: 577px) and (max-width: 992px) {
  .container { padding: 16px; }
  .sidebar { width: 200px; }
}

/* 桌面 */
@media (min-width: 993px) {
  .container { padding: 24px; }
  .sidebar { width: 240px; }
}
```

### 触摸优化

```css
/* 按钮最小触摸区域 */
.btn {
  min-height: 44px;
  min-width: 44px;
}

/* 防止双击缩放 */
* {
  touch-action: manipulation;
}
```

## 性能优化

### 懒加载

```jsx
// 组件懒加载
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

<Suspense fallback={<Spin />}>
  <HeavyComponent />
</Suspense>

// 图片懒加载
<Image src={url} placeholder={<Spin />} />
```

### 防抖节流

```jsx
// 搜索防抖
import { useDebounceFn } from 'ahooks';

const { run: handleSearch } = useDebounceFn(
  (value) => fetchData(value),
  { wait: 300 }
);

<Input.Search onChange={(e) => handleSearch(e.target.value)} />
```

## 相关技能

- [frontend-design](./frontend-design.md) - 前端设计规范
- [code-reviewer](./code-reviewer.md) - 代码审查
