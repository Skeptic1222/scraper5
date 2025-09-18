// NUCLEAR OPTION - Force dashboard content to appear
console.log('NUCLEAR DASHBOARD LOADING...');

// Wait for page to load then force content
setTimeout(() => {
    console.log('NUCLEAR: Forcing dashboard content...');
    
    // Find the main content area and blast the dashboard in there
    const contentArea = document.querySelector('.content-area') || document.querySelector('main') || document.body;
    
    if (contentArea) {
        console.log('NUCLEAR: Found content area, injecting dashboard...');
        
        // Create a big red box that's impossible to miss
        const nuclearDashboard = document.createElement('div');
        nuclearDashboard.style.cssText = `
            position: fixed !important;
            top: 20px !important;
            left: 20px !important;
            right: 20px !important;
            bottom: 20px !important;
            background: #ff0000 !important;
            color: white !important;
            padding: 40px !important;
            z-index: 99999 !important;
            border: 10px solid #00ff00 !important;
            font-size: 24px !important;
            overflow: auto !important;
        `;
        
        nuclearDashboard.innerHTML = `
            <h1 style="color: yellow !important; font-size: 48px !important;">🚨 NUCLEAR DASHBOARD TEST 🚨</h1>
            <p style="font-size: 24px !important;">If you can see this RED BOX with GREEN BORDER, the dashboard system is working!</p>
            <button onclick="this.parentElement.remove()" style="font-size: 20px !important; padding: 10px 20px !important; background: yellow !important; color: black !important; border: none !important; cursor: pointer !important;">Close This Test</button>
            
            <hr style="border: 3px solid yellow !important; margin: 30px 0 !important;">
            
            <h2 style="color: #00ffff !important;">📊 Download Dashboard</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                <div style="background: rgba(0,0,0,0.5); padding: 20px; border: 2px solid yellow;">
                    <h3 style="color: #00ff00;">0</h3>
                    <p>Active Downloads</p>
                </div>
                <div style="background: rgba(0,0,0,0.5); padding: 20px; border: 2px solid yellow;">
                    <h3 style="color: #00ff00;">12</h3>
                    <p>Total Assets</p>
                </div>
                <div style="background: rgba(0,0,0,0.5); padding: 20px; border: 2px solid yellow;">
                    <h3 style="color: #00ff00;">118</h3>
                    <p>Content Sources</p>
                </div>
                <div style="background: rgba(0,0,0,0.5); padding: 20px; border: 2px solid yellow;">
                    <h3 style="color: #00ff00;">0</h3>
                    <p>Queue Length</p>
                </div>
            </div>
            
            <h3 style="color: #ffff00;">Quick Actions</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button style="background: #0066cc; color: white; border: none; padding: 10px 20px; cursor: pointer; font-size: 16px;">🔍 Start Search</button>
                <button style="background: #28a745; color: white; border: none; padding: 10px 20px; cursor: pointer; font-size: 16px;">📁 View Assets</button>
                <button onclick="location.reload()" style="background: #6c757d; color: white; border: none; padding: 10px 20px; cursor: pointer; font-size: 16px;">🔄 Refresh</button>
            </div>
            
            <p style="margin-top: 30px; font-size: 18px; color: #ffff00;">This is the NUCLEAR dashboard test. If you can see this, we know the JavaScript system works!</p>
        `;
        
        document.body.appendChild(nuclearDashboard);
        console.log('NUCLEAR: Dashboard content injected!');
    } else {
        console.error('NUCLEAR: Could not find content area!');
    }
    
}, 1000); // Wait 1 second to ensure page is fully loaded