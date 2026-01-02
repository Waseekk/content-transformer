import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Card, Badge, Button } from '../../components/common';

export function DashboardPage() {
  const { user, logout } = useAuth();

  if (!user) return null;

  const features = [
    {
      title: 'Translation & Enhancement',
      description: 'Translate to Bengali and generate professional news formats',
      icon: '🌐',
      path: '/translation',
      color: 'blue',
    },
    {
      title: 'Articles',
      description: 'Browse and search scraped articles',
      icon: '📰',
      path: '/articles',
      color: 'green',
    },
    {
      title: 'Scraper',
      description: 'Collect latest news from configured sources',
      icon: '🔍',
      path: '/scraper',
      color: 'orange',
    },
  ];

  const colorClasses: Record<string, string> = {
    blue: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
    green: 'from-green-500 to-green-600 hover:from-green-600 hover:to-green-700',
    orange: 'from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Travel News SaaS</h1>
              <p className="text-sm text-gray-600">AI-powered translation & content enhancement</p>
            </div>
            <Button variant="secondary" onClick={logout} size="sm">
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* User Info Card */}
        <Card className="mb-8">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-1">
                Welcome, {user.full_name}!
              </h2>
              <p className="text-sm text-gray-600">{user.email}</p>
              <div className="flex items-center gap-3 mt-4">
                <Badge variant={user.subscription_status === 'active' ? 'success' : 'warning'}>
                  {user.subscription_tier?.toUpperCase()} TIER
                </Badge>
                <Badge variant="info">
                  {user.tokens_remaining.toLocaleString()} / {user.monthly_token_limit.toLocaleString()} Tokens
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-blue-600">
                {user.tokens_remaining.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Tokens Remaining</div>
              <div className="mt-2">
                <div className="w-48 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${(user.tokens_remaining / user.monthly_token_limit) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Features Grid */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Link
                key={feature.path}
                to={feature.path}
                className="group block"
              >
                <div className={`bg-gradient-to-br ${colorClasses[feature.color]} text-white rounded-lg p-6 shadow-lg hover:shadow-xl transition-all transform group-hover:scale-105`}>
                  <div className="text-4xl mb-3">{feature.icon}</div>
                  <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-sm opacity-90">{feature.description}</p>
                  <div className="mt-4 flex items-center text-sm font-medium">
                    Launch →
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-blue-50 to-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600 mb-1">Tokens Used</div>
                <div className="text-2xl font-bold text-blue-600">
                  {user.tokens_used.toLocaleString()}
                </div>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600 mb-1">Account Status</div>
                <div className="text-2xl font-bold text-green-600 capitalize">
                  {user.subscription_status}
                </div>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600 mb-1">Member Since</div>
                <div className="text-lg font-bold text-purple-600">
                  {new Date(user.created_at).toLocaleDateString()}
                </div>
              </div>
              <div className="text-4xl">📅</div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
