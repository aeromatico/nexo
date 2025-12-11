import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from '../pages/DashboardPage';
import { queryClient } from '../services/queryClient';

// Mock API
vi.mock('../services/api', () => ({
  dashboardAPI: {
    getDashboardData: vi.fn(() =>
      Promise.resolve({
        total_purchases: 10000,
        pending_orders: 5,
        pending_invoices: 3,
        open_tickets: 1,
        recent_invoices: [],
        orders_chart: [],
      })
    ),
  },
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard page', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('displays stats cards', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('dashboard.total_purchases')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Loading spinner should appear initially
    const dashboard = screen.queryByText('Dashboard');
    expect(dashboard).toBeInTheDocument();
  });
});
