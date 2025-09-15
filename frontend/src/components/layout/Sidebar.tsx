import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Calendar, 
  DollarSign, 
  HandHeart, 
  Users, 
  Settings,
  TrendingUp
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Events', href: '/events', icon: Calendar },
  { name: 'Budget', href: '/budget', icon: DollarSign },
  { name: 'Pledges', href: '/pledges', icon: HandHeart },
  { name: 'Vendors', href: '/vendors', icon: Users },
  { name: 'Analytics', href: '/analytics', icon: TrendingUp },
  { name: 'Settings', href: '/settings', icon: Settings },
];

interface SidebarProps {
  isOpen: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const location = useLocation();

  return (
    <div className={cn(
      "fixed inset-y-0 left-0 z-50 w-64 bg-surface border-r border-border-subtle transition-transform duration-300",
      "lg:translate-x-0",
      isOpen ? "translate-x-0" : "-translate-x-full"
    )}>
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center px-6 border-b border-border-subtle">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
              <DollarSign className="w-4 h-4 text-accent-foreground" />
            </div>
            <h1 className="text-lg font-semibold text-foreground">Budget Manager</h1>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 hover-lift",
                  isActive
                    ? "bg-accent text-accent-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-surface-elevated"
                )}
              >
                <Icon className={cn(
                  "mr-3 h-4 w-4 flex-shrink-0 transition-colors",
                  isActive 
                    ? "text-accent-foreground" 
                    : "text-muted-foreground group-hover:text-foreground"
                )} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="border-t border-border-subtle p-4">
          <div className="flex items-center space-x-3 text-sm">
            <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
              <span className="text-secondary-foreground font-medium">U</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-foreground font-medium truncate">User Account</p>
              <p className="text-muted-foreground truncate">user@example.com</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};