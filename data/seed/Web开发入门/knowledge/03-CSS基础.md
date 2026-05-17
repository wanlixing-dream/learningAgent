# CSS 基础

## 什么是 CSS

CSS（Cascading Style Sheets）= **层叠样式表**。

如果说 HTML 是网页的"骨架"，CSS 就是"衣服"——决定网页**长什么样**。

## CSS 的基本语法

```css
选择器 {
    属性: 值;
    属性: 值;
}
```

例子：

```css
h1 {
    color: red;           /* 文字颜色 */
    font-size: 32px;      /* 字体大小 */
    text-align: center;   /* 居中对齐 */
}
```

## 三种使用 CSS 的方式

### 1. 行内样式（写在标签上）

```html
<h1 style="color: red;">红色标题</h1>
```

### 2. 内部样式（写在 `<head>` 里）

```html
<head>
    <style>
        h1 { color: red; }
        p { font-size: 16px; }
    </style>
</head>
```

### 3. 外部样式（单独的 .css 文件）⭐推荐

```html
<!-- HTML 文件 -->
<head>
    <link rel="stylesheet" href="style.css">
</head>
```

```css
/* style.css 文件 */
h1 { color: red; }
p { font-size: 16px; }
```

## 常用 CSS 属性

### 文字相关

| 属性 | 作用 | 例子 |
|------|------|------|
| `color` | 文字颜色 | `color: blue;` |
| `font-size` | 字体大小 | `font-size: 20px;` |
| `font-weight` | 加粗 | `font-weight: bold;` |
| `text-align` | 对齐方式 | `text-align: center;` |

### 背景和边框

| 属性 | 作用 | 例子 |
|------|------|------|
| `background-color` | 背景颜色 | `background-color: #f0f0f0;` |
| `border` | 边框 | `border: 1px solid black;` |
| `border-radius` | 圆角 | `border-radius: 10px;` |

### 间距

| 属性 | 作用 | 例子 |
|------|------|------|
| `margin` | 外边距（元素外面） | `margin: 20px;` |
| `padding` | 内边距（元素里面） | `padding: 10px;` |

## 选择器

| 选择器 | 匹配什么 | 例子 |
|--------|---------|------|
| 标签名 | 所有该标签 | `p { color: red; }` |
| `.类名` | 有这个 class 的元素 | `.highlight { color: yellow; }` |
| `#ID名` | 有这个 id 的元素 | `#header { font-size: 24px; }` |

```html
<p class="highlight">这是高亮文字</p>
<p>这是普通文字</p>
```

## 颜色的写法

```css
color: red;                /* 颜色名 */
color: #ff0000;            /* 十六进制 */
color: rgb(255, 0, 0);     /* RGB */
```

常用颜色名：`red` `blue` `green` `black` `white` `gray` `orange` `purple`

## 小测验

1. CSS 中 `margin` 表示什么？
   - A. 文字颜色
   - B. 内边距
   - C. 外边距
   - **答案：C**

2. `.my-class` 选择器匹配什么？
   - A. 所有元素
   - B. id 为 my-class 的元素
   - C. class 为 my-class 的元素
   - **答案：C**
