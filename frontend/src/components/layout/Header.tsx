import React from 'react';
import { Button } from '@/components/ui/button';
import { Menu, Bell, Search } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface HeaderProps {
  onMenuClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { logout } = useAuth();

  return (
    <header className="bg-surface border-b border-border-subtle">
      <div className="flex h-16 items-center px-4 lg:px-6">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="sm"
          className="lg:hidden mr-2"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search events, budgets, pledges..."
              className="w-full pl-10 pr-4 py-2 bg-input border border-input-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring transition-colors"
            />
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-4 ml-4">
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-accent rounded-full flex items-center justify-center">
              <span className="text-xs text-accent-foreground font-medium">3</span>
            </span>
          </Button>

          <Button variant="secondary" size="sm" onClick={logout}>
            Sign Out
          </Button>
        </div>
      </div>
    </header>
  );
};