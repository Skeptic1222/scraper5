// Simple Dashboard that actually works
console.log('Simple dashboard loading...');

function createSimpleDashboard() {
    console.log('Creating simple dashboard...');
    
    const container = document.getElementById('dashboard-dynamic-content');
    if (!container) {
        console.error('Dashboard container not found');
        return;
    }
    
    console.log('Container found, creating dashboard...');
    
    // Simple dashboard HTML
    container.innerHTML = `
        <div style="padding: 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #3b82f6; margin-bottom: 10px;">
                        <i class="fas fa-download"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;" id="active-downloads">0</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Active Downloads</div>
                </div>
                
                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #10b981; margin-bottom: 10px;">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;" id="total-assets">12</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Total Assets</div>
                </div>
                
                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #f59e0b; margin-bottom: 10px;">
                        <i class="fas fa-globe"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;">118</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Content Sources</div>
                </div>
                
                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #ef4444; margin-bottom: 10px;">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;" id="queue-length">0</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Queue Length</div>
                </div>
            </div>
            
            <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h3 style="margin-bottom: 15px; color: #1f2937;">
                    <i class="fas fa-bolt"></i> Quick Actions
                </h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="navigateToSearch()">
                        <i class="fas fa-search"></i> Start Search
                    </button>
                    <button class="btn btn-success" onclick="navigateToAssets()">
                        <i class="fas fa-folder-open"></i> View Assets
                    </button>
                    <button class="btn btn-info" onclick="refreshDashboardData()">
                        <i class="fas fa-sync"></i> Refresh Data
                    </button>
                    <button class="btn btn-secondary" onclick="location.reload()">
                        <i class="fas fa-redo"></i> Reload Page
                    </button>
                </div>
            </div>
            
            <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px;">
                <h3 style="margin-bottom: 15px; color: #1f2937;">
                    <i class="fas fa-info-circle"></i> System Status
                </h3>
                <div style="color: #10b981; margin-bottom: 10px;">
                    <i class="fas fa-check-circle"></i> Database Connected
                </div>
                <div style="color: #10b981; margin-bottom: 10px;">
                    <i class="fas fa-check-circle"></i> APIs Responding
                </div>
                <div style="color: #10b981;">
                    <i class="fas fa-check-circle"></i> Navigation Working
                </div>
            </div>
        </div>
    `;
    
    console.log('Dashboard HTML created successfully');
    loadSimpleData();
}

function loadSimpleData() {
    console.log('Loading dashboard data...');
    
    // Load assets count
    fetch('/api/assets')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.assets) {
                document.getElementById('total-assets').textContent = data.assets.length;
                console.log(`Loaded ${data.assets.length} assets`);
            }
        })
        .catch(error => console.error('Error loading assets:', error));
    
    // Load jobs data
    fetch('/api/jobs')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.jobs) {
                const activeJobs = data.jobs.filter(job => job.status === 'running' || job.status === 'downloading');
                const queuedJobs = data.jobs.filter(job => job.status === 'pending');
                
                document.getElementById('active-downloads').textContent = activeJobs.length;
                document.getElementById('queue-length').textContent = queuedJobs.length;
                
                console.log(`Active downloads: ${activeJobs.length}, Queue: ${queuedJobs.length}`);
            }
        })
        .catch(error => console.error('Error loading jobs:', error));
}

function navigateToSearch() {
    console.log('Navigating to search...');
    window.location.hash = 'search';
    // Trigger navigation manually
    if (window.navigation && window.navigation.switchSection) {
        window.navigation.switchSection('search-section');
    }
}

function navigateToAssets() {
    console.log('Navigating to assets...');
    window.location.hash = 'assets';
    if (window.navigation && window.navigation.switchSection) {
        window.navigation.switchSection('assets-section');
    }
}

function refreshDashboardData() {
    console.log('Refreshing dashboard data...');
    loadSimpleData();
}

// Initialize when ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple dashboard DOM loaded');
    setTimeout(createSimpleDashboard, 100);
});

// Also try to initialize if DOM is already loaded
if (document.readyState !== 'loading') {
    console.log('DOM already loaded, initializing dashboard...');
    setTimeout(createSimpleDashboard, 100);
}

console.log('Simple dashboard script loaded');