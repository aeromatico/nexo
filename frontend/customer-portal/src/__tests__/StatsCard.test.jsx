import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatsCard from '../components/Dashboard/StatsCard';

describe('StatsCard', () => {
  it('renders title and value', () => {
    render(
      <StatsCard
        title="Total Compras"
        value="Bs. 10,000"
        icon="shopping-cart"
      />
    );

    expect(screen.getByText('Total Compras')).toBeInTheDocument();
    expect(screen.getByText('Bs. 10,000')).toBeInTheDocument();
  });

  it('displays trend indicator when provided', () => {
    render(
      <StatsCard
        title="Total Compras"
        value="Bs. 10,000"
        trend={15}
        icon="shopping-cart"
      />
    );

    expect(screen.getByText('15%')).toBeInTheDocument();
  });

  it('renders with different icon types', () => {
    const { rerender } = render(
      <StatsCard
        title="Test"
        value="100"
        icon="package"
      />
    );

    expect(screen.getByText('Test')).toBeInTheDocument();

    rerender(
      <StatsCard
        title="Test2"
        value="200"
        icon="file-text"
      />
    );

    expect(screen.getByText('Test2')).toBeInTheDocument();
  });
});
