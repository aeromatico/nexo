import React, { useState } from 'react';

export default function ProductListPage() {
  const [filters, setFilters] = useState({});

  return (
    <div className="flex gap-6">
      {/* Sidebar Filters */}
      <aside className="w-64">
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <h3 className="font-bold text-lg mb-4">Categorías</h3>
            {/* Filter options */}
          </div>
        </div>
      </aside>

      {/* Products Grid */}
      <main className="flex-1">
        <div className="grid grid-cols-3 gap-6">
          {/* Product cards */}
        </div>
      </main>
    </div>
  );
}
