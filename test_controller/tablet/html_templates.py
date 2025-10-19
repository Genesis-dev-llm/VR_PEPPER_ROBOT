"""
Professional HTML/CSS Templates for Pepper's Tablet
High-quality, modern UI designs.
"""

def get_status_display_html(action, action_detail, battery, mode):
    """Generate HTML for status + action display."""
    
    # Battery color based on level
    if battery >= 60:
        battery_color = "#4ade80"  # Green
    elif battery >= 30:
        battery_color = "#fbbf24"  # Yellow
    else:
        battery_color = "#f87171"  # Red
    
    # Mode text
    mode_text = "CONTINUOUS" if mode else "INCREMENTAL"
    
    # Action icon mapping
    action_icons = {
        "Ready": "🤖",
        "Moving Forward": "⬆️",
        "Moving Backward": "⬇️",
        "Strafing Left": "⬅️",
        "Strafing Right": "➡️",
        "Rotating Left": "↶",
        "Rotating Right": "↷",
        "Wave": "👋",
        "Special Dance": "💃",
        "Robot Dance": "🤖",
        "Moonwalk": "🌙",
        "Looking Around": "👀",
        "Moving Arms": "💪",
        "Hello": "👋",
        "Emergency Stop": "🚨",
        "Low Battery": "🔋"
    }
    
    icon = action_icons.get(action, "🤖")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }}
            
            .header {{
                position: absolute;
                top: 20px;
                left: 20px;
                font-size: 24px;
                font-weight: 600;
                opacity: 0.9;
            }}
            
            .action-card {{
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 60px 80px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: fadeIn 0.5s ease-in-out;
                max-width: 90%;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .action-icon {{
                font-size: 120px;
                margin-bottom: 20px;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
            }}
            
            .action-text {{
                font-size: 56px;
                font-weight: bold;
                margin-bottom: 15px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            .action-detail {{
                font-size: 32px;
                opacity: 0.9;
                font-weight: 300;
            }}
            
            .status-bar {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                padding: 20px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 24px;
            }}
            
            .battery {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .battery-bar {{
                width: 150px;
                height: 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            .battery-fill {{
                height: 100%;
                background: {battery_color};
                width: {battery}%;
                transition: width 0.3s ease;
            }}
            
            .mode-badge {{
                background: rgba(255, 255, 255, 0.2);
                padding: 8px 16px;
                border-radius: 12px;
                font-size: 20px;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="header">🤖 PEPPER</div>
        
        <div class="action-card">
            <div class="action-icon">{icon}</div>
            <div class="action-text">{action.upper()}</div>
            <div class="action-detail">{action_detail}</div>
        </div>
        
        <div class="status-bar">
            <div class="battery">
                <span>🔋 {battery}%</span>
                <div class="battery-bar">
                    <div class="battery-fill"></div>
                </div>
            </div>
            <div class="mode-badge">{mode_text}</div>
        </div>
    </body>
    </html>
    """
    
    return html


def get_camera_mirror_html(camera_url, action):
    """Generate HTML for camera feed mirror."""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: #000;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px 30px;
                font-size: 28px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }}
            
            .camera-container {{
                flex: 1;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                background: #1a1a1a;
            }}
            
            .camera-feed {{
                max-width: 100%;
                max-height: 100%;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}
            
            .action-overlay {{
                position: absolute;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(102, 126, 234, 0.9);
                backdrop-filter: blur(10px);
                padding: 15px 30px;
                border-radius: 20px;
                font-size: 24px;
                font-weight: 600;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.5s ease-in-out;
            }}
            
            @keyframes slideUp {{
                from {{ opacity: 0; transform: translate(-50%, 20px); }}
                to {{ opacity: 1; transform: translate(-50%, 0); }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            📹 PEPPER'S VIEW
        </div>
        
        <div class="camera-container">
            <img class="camera-feed" src="{camera_url}" alt="Camera Feed">
        </div>
        
        <div class="action-overlay">
            Current: {action}
        </div>
    </body>
    </html>
    """
    
    return html


def get_greeting_html(greeting_image_url=None, greeting_text="Hello!"):
    """Generate HTML for greeting display."""
    
    if greeting_image_url:
        content = f'<img class="greeting-image" src="{greeting_image_url}" alt="Greeting">'
    else:
        content = f'<div class="greeting-text">{greeting_text}</div>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }}
            
            .greeting-container {{
                text-align: center;
                animation: bounceIn 0.8s ease-in-out;
            }}
            
            @keyframes bounceIn {{
                0% {{ opacity: 0; transform: scale(0.3); }}
                50% {{ transform: scale(1.05); }}
                70% {{ transform: scale(0.9); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            
            .greeting-text {{
                font-size: 120px;
                font-weight: bold;
                text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);
            }}
            
            .greeting-image {{
                max-width: 80%;
                max-height: 80vh;
                border-radius: 30px;
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
                border: 4px solid rgba(255, 255, 255, 0.3);
            }}
        </style>
    </head>
    <body>
        <div class="greeting-container">
            {content}
        </div>
    </body>
    </html>
    """
    
    return html