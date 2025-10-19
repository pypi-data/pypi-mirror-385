import os
import sys
import argparse
import http.server
import socketserver
import webbrowser
from datetime import datetime

# 支持的图片格式
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"}

def is_image_file(filename):
    """检查文件是否为图片"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in IMAGE_EXTENSIONS

def get_images_from_directory(directory):
    """获取目录中的所有图片文件"""
    images = []
    for root, _, files in os.walk(directory):
        for file in files:
            if is_image_file(file):
                # 计算相对路径，用于HTML中引用
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                images.append(rel_path)
    return images

def generate_html(directory, images):
    """生成图片预览HTML"""
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>图片预览 - {os.path.basename(directory)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background-color: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        
        header {{
            margin-bottom: 30px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .info {{,
            color: #7f8c8d;
            font-size: 14px;
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .image-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        
        .image-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .image-container {{
            width: 100%;
            height: 200px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f0f0f0;
        }}
        
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}
        
        .image-card:hover .image-container img {{
            transform: scale(1.05);
        }}
        
        .image-info {{
            padding: 12px;
        }}
        
        .image-name {{
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: #2c3e50;
        }}
        
        /* 模态框样式 */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }}
        
        .modal-content {{
            max-width: 90%;
            max-height: 90%;
        }}
        
        .modal-content img {{
            max-width: 100%;
            max-height: 90vh;
            object-fit: contain;
        }}
        
        .close {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }}
        
        .close:hover {{
            color: #bbb;
        }}
        
        @media (max-width: 768px) {{
            .gallery {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }}
            
            .image-container {{
                height: 150px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>图片文件夹预览</h1>
        <p class="info">文件夹: {os.path.basename(directory)} | 图片数量: {len(images)} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </header>
    
    <div class="gallery">
'''
    
    # 添加图片卡片
    for img_path in images:
        img_name = os.path.basename(img_path)
        html_content += f'''
        <div class="image-card" onclick="openModal('{img_path}')">
            <div class="image-container">
                <img src="{img_path}" alt="{img_name}">
            </div>
            <div class="image-info">
                <div class="image-name">{img_name}</div>
            </div>
        </div>
'''
    
    # 添加页脚和JavaScript
    html_content += f'''
    </div>
    
    <!-- 模态框 -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="预览图片">
        </div>
    </div>
    
    <script>
        const modal = document.getElementById('imageModal');
        const modalImg = document.getElementById('modalImage');
        
        function openModal(imgSrc) {{
            modal.style.display = 'flex';
            modalImg.src = imgSrc;
            document.body.style.overflow = 'hidden';
        }}
        
        function closeModal() {{
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }}
        
        // 按ESC键关闭模态框
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape' && modal.style.display === 'flex') {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>
'''
    
    return html_content

def get_local_ip():
    """获取本机IP地址"""
    try:
        import socket
        # 创建一个UDP套接字连接到外部地址以获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'localhost'

def start_server(directory, port=8000):
    """启动HTTP服务器"""
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    
    # 绑定到0.0.0.0以支持外网访问
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        local_ip = get_local_ip()
        print(f"服务器已启动:")
        print(f"  - 本地访问: http://localhost:{port}")
        print(f"  - 外网访问: http://{local_ip}:{port}")
        print("按 Ctrl+C 停止服务器")
        
        try:
            # 尝试自动打开浏览器（使用本地地址）
            webbrowser.open(f"http://localhost:{port}")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
            httpd.server_close()

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='图片文件夹可视化工具')
    parser.add_argument('-d', '--directory', required=True, help='要可视化的图片文件夹路径')
    parser.add_argument('-p', '--port', type=int, default=8000, help='服务器端口 (默认: 8000)')
    args = parser.parse_args()
    
    # 验证目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)
    
    # 获取所有图片
    images = get_images_from_directory(args.directory)
    
    if not images:
        print(f"警告: 目录 '{args.directory}' 中没有找到支持的图片文件")
    else:
        print(f"找到 {len(images)} 张图片")
    
    # 生成index.html文件
    html_content = generate_html(args.directory, images)
    index_path = os.path.join(args.directory, 'index.html')
    
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML预览文件已生成: {index_path}")
    except Exception as e:
        print(f"生成HTML文件失败: {e}")
        sys.exit(1)
    
    # 启动服务器
    start_server(args.directory, args.port)

if __name__ == "__main__":
    main()