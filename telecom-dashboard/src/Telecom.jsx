import { useState, useEffect } from 'react';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Shield,
  Activity,
  Search,
  Filter,
  Download,
  RefreshCw,
  Bell,
  Eye,
  BarChart3,
  PieChart,
  Calendar,
  Phone,
  Mail,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import React from 'react';

const Telecom = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [customers, setCustomers] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('all');
  const [filterAnomaly, setFilterAnomaly] = useState('all');
  const [error, setError] = useState(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    type: 'comprehensive',
    frequency: 'weekly',
    recipients: ''
  });
  const [showInvestigationModal, setShowInvestigationModal] = useState(false);
  const [investigationData, setInvestigationData] = useState(null);
  const [investigationLoading, setInvestigationLoading] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Close notifications dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showNotifications && !event.target.closest('.notification-dropdown')) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showNotifications]);

  // const fetchData = async () => {
  //   try {
  //     const customerRes = await fetch(`${import.meta.env.VITE_BASE_URL}/customers`)
  //     console.log(customerRes.body)
  //   } catch (err) {
  //     console.error(err)
  //   }
  // }

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching data from:', import.meta.env.VITE_BASE_URL);

      const [customersRes, analyticsRes, alertsRes, notificationsRes] = await Promise.all([
        fetch(`${import.meta.env.VITE_BASE_URL}/api/customers`).catch(err => {
          console.error('Failed to fetch customers:', err);
          return null;
        }),
        fetch(`${import.meta.env.VITE_BASE_URL}/api/analytics`).catch(err => {
          console.error('Failed to fetch analytics:', err);
          return null;
        }),
        fetch(`${import.meta.env.VITE_BASE_URL}/api/alerts`).catch(err => {
          console.error('Failed to fetch alerts:', err);
          return null;
        }),
        fetch(`${import.meta.env.VITE_BASE_URL}/api/notifications`).catch(err => {
          console.error('Failed to fetch notifications:', err);
          return null;
        })
      ]);

      console.log('Responses received:', { customersRes, analyticsRes, alertsRes, notificationsRes });

      // Handle customers response
      if (customersRes && customersRes.ok) {
        const customersData = await customersRes.json();
        console.log('Customers data:', customersData);
        setCustomers(customersData.customers || []);
      } else {
        console.error('Failed to fetch customers');
        setCustomers([]);
      }

      // Handle analytics response
      if (analyticsRes && analyticsRes.ok) {
        const analyticsData = await analyticsRes.json();
        console.log('Analytics data:', analyticsData);
        setAnalytics(analyticsData);
      } else {
        console.error('Failed to fetch analytics');
        // Set default analytics data
        setAnalytics({
          riskMetrics: {
            totalCustomers: 0,
            averageChurnProb: 0,
            anomalyRate: 0,
            highRiskRevenue: 0
          },
          churnDistribution: { high: 0, medium: 0, low: 0 },
          anomalyDistribution: { normal: 0 },
          monthlyTrends: [],
          topFeatures: []
        });
      }

      // Handle alerts response
      if (alertsRes && alertsRes.ok) {
        const alertsData = await alertsRes.json();
        console.log('Alerts data:', alertsData);
        setAlerts(alertsData.alerts || []);
      } else {
        console.error('Failed to fetch alerts');
        setAlerts([]);
      }

      // Handle notifications response
      if (notificationsRes && notificationsRes.ok) {
        const notificationsData = await notificationsRes.json();
        console.log('Notifications data:', notificationsData);
        setNotifications(notificationsData.notifications || []);
      } else {
        console.error('Failed to fetch notifications');
        setNotifications([]);
      }

    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to connect to the server. Please ensure the backend is running on port 5000.');

      // Set default values to prevent errors
      setCustomers([]);
      setAlerts([]);
      if (!analytics) {
        setAnalytics({
          riskMetrics: {
            totalCustomers: 0,
            averageChurnProb: 0,
            anomalyRate: 0,
            highRiskRevenue: 0
          },
          churnDistribution: { high: 0, medium: 0, low: 0 },
          anomalyDistribution: { normal: 0 },
          monthlyTrends: [],
          topFeatures: []
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(customer => {
    if (!customer) return false;

    const customerId = customer.id || '';
    const anomalyType = customer.anomalyType || 'Normal';
    const riskLevel = customer.riskLevel || 'Low';
    const isAnomaly = customer.isAnomaly || false;

    const matchesSearch = customerId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      anomalyType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = filterRisk === 'all' || riskLevel.toLowerCase() === filterRisk;
    const matchesAnomaly = filterAnomaly === 'all' ||
      (filterAnomaly === 'anomaly' && isAnomaly) ||
      (filterAnomaly === 'normal' && !isAnomaly);

    return matchesSearch && matchesRisk && matchesAnomaly;
  });

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'High': return 'text-red-600 bg-red-50 border-red-200';
      case 'Medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getAnomalyColor = (type) => {
    if (type === 'Normal') return 'text-green-600 bg-green-50';
    return 'text-red-600 bg-red-50';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  // Safe alert counting functions
  const getAlertCount = (severity) => {
    if (!Array.isArray(alerts)) return 0;
    return alerts.filter(a => a && a.severity === severity).length;
  };

  const getActionRequiredCount = () => {
    if (!Array.isArray(alerts)) return 0;
    return alerts.filter(a => a && a.actionRequired).length;
  };

  const handleExportCustomers = async () => {
    try {
      setExportLoading(true);
      const response = await fetch(`${import.meta.env.VITE_BASE_URL}/api/export/customers`);
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `customer_data_export_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export customer data. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setReportLoading(true);
      const response = await fetch(`${import.meta.env.VITE_BASE_URL}/api/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'comprehensive'
        })
      });
      
      if (!response.ok) {
        throw new Error('Report generation failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `analytics_report_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Report generation error:', error);
      alert('Failed to generate report. Please try again.');
    } finally {
      setReportLoading(false);
    }
  };

  const handleScheduleReport = async () => {
    try {
      const recipients = scheduleForm.recipients.split(',').map(email => email.trim()).filter(email => email);
      
      const response = await fetch(`${import.meta.env.VITE_BASE_URL}/api/reports/schedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: scheduleForm.type,
          frequency: scheduleForm.frequency,
          recipients: recipients
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to schedule report');
      }
      
      const result = await response.json();
      alert('Report scheduled successfully!');
      setShowScheduleModal(false);
      setScheduleForm({
        type: 'comprehensive',
        frequency: 'weekly',
        recipients: ''
      });
      
    } catch (error) {
      console.error('Schedule error:', error);
      alert('Failed to schedule report. Please try again.');
    }
  };

  const handleInvestigateAlert = async (alertId) => {
    try {
      setInvestigationLoading(true);
      setShowInvestigationModal(true);
      
      const response = await fetch(`${import.meta.env.VITE_BASE_URL}/api/alerts/${alertId}/investigate`);
      
      if (!response.ok) {
        throw new Error('Failed to load investigation data');
      }
      
      const data = await response.json();
      setInvestigationData(data);
      
    } catch (error) {
      console.error('Investigation error:', error);
      alert('Failed to load investigation data. Please try again.');
      setShowInvestigationModal(false);
    } finally {
      setInvestigationLoading(false);
    }
  };

  const handleAlertAction = async (alertId, action, notes = '') => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BASE_URL}/api/alerts/${alertId}/actions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: action,
          notes: notes
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to take action');
      }
      
      const result = await response.json();
      alert(`Alert ${action}d successfully!`);
      
      // Refresh alerts
      fetchData();
      setShowInvestigationModal(false);
      
    } catch (error) {
      console.error('Action error:', error);
      alert('Failed to take action. Please try again.');
    }
  };

  const markNotificationAsRead = async (notificationId) => {
    try {
      await fetch(`${import.meta.env.VITE_BASE_URL}/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      // Update local state
      const updatedNotifications = notifications.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      );
      setNotifications(updatedNotifications);
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllNotificationsAsRead = async () => {
    try {
      await fetch(`${import.meta.env.VITE_BASE_URL}/api/notifications/mark-all-read`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      // Update local state
      const updatedNotifications = notifications.map(n => ({ ...n, read: true }));
      setNotifications(updatedNotifications);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  if (loading && !analytics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
          <span className="text-lg text-gray-600">Loading enterprise dashboard...</span>
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600">{error}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-full px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <Shield className="h-8 w-8 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">TelecomGuard Pro</h1>
                  <p className="text-sm text-gray-500">Enterprise Churn & Anomaly Detection Platform</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative notification-dropdown">
                <Bell 
                  className="h-6 w-6 text-gray-600 cursor-pointer hover:text-gray-800" 
                  onClick={() => setShowNotifications(!showNotifications)}
                />
                {Array.isArray(notifications) && notifications.filter(n => !n.read).length > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {notifications.filter(n => !n.read).length}
                  </span>
                )}
                
                {/* Notifications Dropdown */}
                {showNotifications && (
                  <div className="absolute right-0 top-8 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
                    <div className="p-4 border-b border-gray-200">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
                        <button
                          onClick={markAllNotificationsAsRead}
                          className="text-sm text-blue-600 hover:text-blue-800"
                        >
                          Mark all read
                        </button>
                      </div>
                    </div>
                    
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.length > 0 ? (
                        notifications.map(notification => (
                          <div
                            key={notification.id}
                            className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                              !notification.read ? 'bg-blue-50' : ''
                            }`}
                            onClick={() => markNotificationAsRead(notification.id)}
                          >
                            <div className="flex items-start space-x-3">
                              <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                                notification.severity === 'critical' ? 'bg-red-500' :
                                notification.severity === 'high' ? 'bg-orange-500' :
                                notification.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                              }`}></div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                  <p className={`text-sm font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-600'}`}>
                                    {notification.title}
                                  </p>
                                  {!notification.read && (
                                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                  )}
                                </div>
                                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                                  {notification.message}
                                </p>
                                <div className="flex items-center justify-between mt-2">
                                  <p className="text-xs text-gray-400">
                                    {new Date(notification.timestamp).toLocaleString()}
                                  </p>
                                  {notification.actionRequired && (
                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                      Action Required
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="p-8 text-center text-gray-500">
                          <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                          <p className="text-sm">No notifications</p>
                        </div>
                      )}
                    </div>
                    
                    {notifications.length > 0 && (
                      <div className="p-3 border-t border-gray-200 bg-gray-50">
                        <button
                          onClick={() => {
                            setActiveTab('alerts');
                            setShowNotifications(false);
                          }}
                          className="w-full text-center text-sm text-blue-600 hover:text-blue-800 font-medium"
                        >
                          View All Alerts
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <button
                onClick={fetchData}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-full px-6">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'customers', label: 'Customer Risk Monitor', icon: Users },
              { id: 'alerts', label: 'Active Alerts', icon: AlertTriangle },
              { id: 'analytics', label: 'Advanced Analytics', icon: Activity }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-4 border-b-2 transition-colors ${activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
              >
                <tab.icon className="h-5 w-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Error Message */}
      {error && (
        <div className="max-w-full px-6 py-4">
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              <p className="text-yellow-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-full px-6 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && analytics && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Total Customers</p>
                    <p className="text-3xl font-bold text-gray-900">
                      {(analytics.riskMetrics?.totalCustomers || 0).toLocaleString()}
                    </p>
                  </div>
                  <Users className="h-12 w-12 text-blue-600" />
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Avg Churn Risk</p>
                    <p className="text-3xl font-bold text-orange-600">
                      {((analytics.riskMetrics?.averageChurnProb || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <TrendingDown className="h-12 w-12 text-orange-600" />
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Anomaly Rate</p>
                    <p className="text-3xl font-bold text-red-600">
                      {((analytics.riskMetrics?.anomalyRate || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <AlertTriangle className="h-12 w-12 text-red-600" />
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">High Risk Revenue</p>
                    <p className="text-3xl font-bold text-green-600">
                      ${(analytics.riskMetrics?.highRiskRevenue || 0).toLocaleString()}
                    </p>
                  </div>
                  <DollarSign className="h-12 w-12 text-green-600" />
                </div>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Churn Risk Distribution */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Churn Risk Distribution</h3>
                <div className="space-y-4">
                  {Object.entries(analytics.churnDistribution || {}).map(([risk, count]) => {
                    const totalCustomers = analytics.riskMetrics?.totalCustomers || 1;
                    const percentage = ((count / totalCustomers) * 100).toFixed(1);
                    return (
                      <div key={risk} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full ${risk === 'high' ? 'bg-red-500' :
                            risk === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`}></div>
                          <span className="capitalize font-medium">{risk} Risk</span>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-semibold">{count.toLocaleString()}</div>
                          <div className="text-sm text-gray-500">{percentage}%</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Anomaly Types */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Anomaly Detection Overview</h3>
                <div className="space-y-3">
                  {Object.entries(analytics.anomalyDistribution || {}).map(([type, count]) => {
                    if (count === 0) return null;
                    return (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">
                          {type.replace('_', ' ')}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${type === 'normal' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                          {count}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Monthly Trends */}
            {analytics.monthlyTrends && analytics.monthlyTrends.length > 0 && (
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Trends</h3>
                <div className="overflow-x-auto">
                  <div className="flex space-x-8 min-w-max">
                    {analytics.monthlyTrends.map(month => (
                      <div key={month.month} className="text-center">
                        <div className="text-sm font-medium text-gray-500">{month.month}</div>
                        <div className="mt-2 space-y-1">
                          <div className="text-lg font-semibold text-orange-600">
                            {((month.churnRate || 0) * 100).toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-500">Churn</div>
                          <div className="text-sm font-medium text-red-600">
                            {((month.anomalyRate || 0) * 100).toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-500">Anomaly</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Customers Tab */}
        {activeTab === 'customers' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center space-x-2">
                  <Search className="h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search customers..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <select
                  value={filterRisk}
                  onChange={(e) => setFilterRisk(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Risk Levels</option>
                  <option value="high">High Risk</option>
                  <option value="medium">Medium Risk</option>
                  <option value="low">Low Risk</option>
                </select>

                <select
                  value={filterAnomaly}
                  onChange={(e) => setFilterAnomaly(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Customers</option>
                  <option value="anomaly">Anomalies Only</option>
                  <option value="normal">Normal Only</option>
                </select>

                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <Filter className="h-4 w-4" />
                  <span>Showing {filteredCustomers.length} of {customers.length} customers</span>
                </div>
              </div>
            </div>

            {/* Customer Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              {filteredCustomers.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Churn Probability</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Anomaly Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Monthly Charges</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tenure</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredCustomers.slice(0, 20).map(customer => (
                        <tr key={customer.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{customer.id}</div>
                              <div className="text-sm text-gray-500">
                                Age: {customer.age || 'N/A'} • {customer.contractType || 'N/A'}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(customer.riskLevel)}`}>
                              {customer.riskLevel}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="text-sm font-medium text-gray-900">
                                {((customer.churnProbability || 0) * 100).toFixed(1)}%
                              </div>
                              <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${customer.churnProbability > 0.7 ? 'bg-red-500' :
                                    customer.churnProbability > 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                                    }`}
                                  style={{ width: `${(customer.churnProbability || 0) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getAnomalyColor(customer.anomalyType || 'Normal')}`}>
                              {customer.isAnomaly ? customer.anomalyType : 'Normal'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${(customer.monthlyCharges || 0).toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {(customer.tenure || 0).toFixed(1)} months
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                            <button className="text-blue-600 hover:text-blue-900">
                              <Eye className="h-4 w-4" />
                            </button>
                            <button className="text-green-600 hover:text-green-900">
                              <Phone className="h-4 w-4" />
                            </button>
                            <button className="text-gray-600 hover:text-gray-900">
                              <Mail className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-8 text-center text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No customers found matching your criteria</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="space-y-6">
            {/* Alert Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3">
                  <AlertCircle className="h-8 w-8 text-red-500" />
                  <div>
                    <p className="text-2xl font-bold text-red-600">{getAlertCount('critical')}</p>
                    <p className="text-sm text-gray-500">Critical</p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="h-8 w-8 text-orange-500" />
                  <div>
                    <p className="text-2xl font-bold text-orange-600">{getAlertCount('high')}</p>
                    <p className="text-sm text-gray-500">High</p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                  <div>
                    <p className="text-2xl font-bold text-yellow-600">{getAlertCount('medium')}</p>
                    <p className="text-sm text-gray-500">Medium</p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="text-2xl font-bold text-gray-900">{getActionRequiredCount()}</p>
                    <p className="text-sm text-gray-500">Action Required</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Alerts List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Active Alerts</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {Array.isArray(alerts) && alerts.length > 0 ? (
                  alerts.map(alert => (
                    <div key={alert.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          <div className={`p-2 rounded-lg ${getSeverityColor(alert.severity)}`}>
                            {alert.type === 'high_churn_risk' ? <TrendingDown className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
                          </div>
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">{alert.message}</h4>
                            <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                              <span className="flex items-center space-x-1">
                                <Clock className="h-4 w-4" />
                                <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                              </span>
                              <span className="capitalize">{alert.type.replace('_', ' ')}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {alert.actionRequired && (
                            <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                              Action Required
                            </span>
                          )}
                          <button 
                            onClick={() => handleInvestigateAlert(alert.id)}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            Investigate
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    <Bell className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No active alerts at this time</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            {/* Feature Importance */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Risk Factors</h3>
              {analytics.topFeatures && analytics.topFeatures.length > 0 ? (
                <div className="space-y-3">
                  {analytics.topFeatures.slice(0, 8).map((feature, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {feature.feature.replace('_', ' ')}
                      </span>
                      <div className="flex items-center space-x-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(feature.importance * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600 min-w-[60px] text-right">
                          {(feature.importance * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No feature importance data available</p>
                </div>
              )}
            </div>

            {/* Export Options */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Export & Reports</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button 
                  onClick={handleExportCustomers}
                  disabled={exportLoading}
                  className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {exportLoading ? (
                    <RefreshCw className="h-5 w-5 text-gray-600 animate-spin" />
                  ) : (
                    <Download className="h-5 w-5 text-gray-600" />
                  )}
                  <span className="text-gray-600">
                    {exportLoading ? 'Exporting...' : 'Export Customer Data'}
                  </span>
                </button>
                <button 
                  onClick={handleGenerateReport}
                  disabled={reportLoading}
                  className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {reportLoading ? (
                    <RefreshCw className="h-5 w-5 text-gray-600 animate-spin" />
                  ) : (
                    <BarChart3 className="h-5 w-5 text-gray-600" />
                  )}
                  <span className="text-gray-600">
                    {reportLoading ? 'Generating...' : 'Generate Analytics Report'}
                  </span>
                </button>
                <button 
                  onClick={() => setShowScheduleModal(true)}
                  className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
                >
                  <Calendar className="h-5 w-5 text-gray-600" />
                  <span className="text-gray-600">Schedule Report</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Schedule Report Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Schedule Report</h3>
              <button
                onClick={() => setShowScheduleModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Report Type
                </label>
                <select
                  value={scheduleForm.type}
                  onChange={(e) => setScheduleForm({...scheduleForm, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="comprehensive">Comprehensive Analytics</option>
                  <option value="risk_analysis">Risk Analysis</option>
                  <option value="anomaly_report">Anomaly Report</option>
                  <option value="executive_summary">Executive Summary</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Frequency
                </label>
                <select
                  value={scheduleForm.frequency}
                  onChange={(e) => setScheduleForm({...scheduleForm, frequency: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Recipients (comma-separated emails)
                </label>
                <textarea
                  value={scheduleForm.recipients}
                  onChange={(e) => setScheduleForm({...scheduleForm, recipients: e.target.value})}
                  placeholder="admin@company.com, manager@company.com"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowScheduleModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleScheduleReport}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Schedule Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Investigation Modal */}
      {showInvestigationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Alert Investigation</h2>
              <button
                onClick={() => setShowInvestigationModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>
            
            {investigationLoading ? (
              <div className="p-8 text-center">
                <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-600">Loading investigation data...</p>
              </div>
            ) : investigationData ? (
              <div className="p-6 space-y-6">
                {/* Customer Profile */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Customer Profile</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Customer ID</p>
                      <p className="font-medium">{investigationData.customerProfile.id}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Risk Level</p>
                      <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(investigationData.customerProfile.riskLevel)}`}>
                        {investigationData.customerProfile.riskLevel}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Churn Probability</p>
                      <p className="font-medium text-red-600">{(investigationData.customerProfile.churnProbability * 100).toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Monthly Charges</p>
                      <p className="font-medium">${investigationData.customerProfile.monthlyCharges}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Tenure</p>
                      <p className="font-medium">{investigationData.customerProfile.tenure} months</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Complaints</p>
                      <p className="font-medium">{investigationData.customerProfile.complaints}</p>
                    </div>
                  </div>
                </div>

                {/* Risk Factors */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Risk Factors</h3>
                  <div className="space-y-3">
                    {investigationData.riskFactors.map((factor, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
                        <div>
                          <p className="font-medium text-red-800">{factor.factor}</p>
                          <p className="text-sm text-red-600">{factor.description}</p>
                        </div>
                        <div className="text-right">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            factor.impact === 'High' ? 'bg-red-100 text-red-800' :
                            factor.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {factor.impact} Impact
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Recommended Actions</h3>
                  <div className="space-y-3">
                    {investigationData.recommendations.map((rec, index) => (
                      <div key={index} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{rec.action}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            rec.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                            rec.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {rec.priority}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Timeline: {rec.timeline}</span>
                          <span>Impact: {rec.expectedImpact}</span>
                          <span>Cost: {rec.cost}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Historical Data */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Historical Trends</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Charges</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Data Usage</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Complaints</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Churn Risk</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {investigationData.historicalData.map((month, index) => (
                          <tr key={index}>
                            <td className="px-4 py-2 text-sm text-gray-900">{month.month}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">${month.monthlyCharges}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{month.dataUsage} GB</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{month.complaints}</td>
                            <td className="px-4 py-2 text-sm">
                              <span className={`px-2 py-1 rounded text-xs ${
                                month.churnProbability > 0.7 ? 'bg-red-100 text-red-800' :
                                month.churnProbability > 0.4 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {(month.churnProbability * 100).toFixed(1)}%
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Similar Cases */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Similar Cases</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {investigationData.similarCases.map((case_, index) => (
                      <div key={index} className="p-3 border border-gray-200 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900">{case_.customerId}</span>
                          <span className="text-sm text-gray-500">{(case_.similarity * 100).toFixed(0)}% similar</span>
                        </div>
                        <div className="text-sm text-gray-600">
                          <p>Risk: {(case_.churnProbability * 100).toFixed(1)}%</p>
                          <p>Outcome: <span className={case_.outcome === 'Retained' ? 'text-green-600' : 'text-red-600'}>{case_.outcome}</span></p>
                          <p>Action: {case_.actionTaken}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => handleAlertAction(investigationData.alertId, 'resolve', 'Investigated and resolved')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Resolve Alert
                  </button>
                  <button
                    onClick={() => handleAlertAction(investigationData.alertId, 'escalate', 'Escalated for further review')}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                  >
                    Escalate
                  </button>
                  <button
                    onClick={() => setShowInvestigationModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Failed to load investigation data</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Telecom;