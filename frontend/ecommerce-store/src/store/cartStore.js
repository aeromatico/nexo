import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],

      addItem: (product, quantity = 1) =>
        set((state) => {
          const existingItem = state.items.find(item => item.item_code === product.item_code);
          if (existingItem) {
            return {
              items: state.items.map(item =>
                item.item_code === product.item_code
                  ? { ...item, quantity: item.quantity + quantity }
                  : item
              )
            };
          }
          return {
            items: [...state.items, { ...product, quantity }]
          };
        }),

      removeItem: (itemCode) =>
        set((state) => ({
          items: state.items.filter(item => item.item_code !== itemCode)
        })),

      updateQuantity: (itemCode, quantity) =>
        set((state) => ({
          items: quantity <= 0
            ? state.items.filter(item => item.item_code !== itemCode)
            : state.items.map(item =>
                item.item_code === itemCode
                  ? { ...item, quantity }
                  : item
              )
        })),

      clearCart: () => set({ items: [] }),

      getTotal: () => {
        const { items } = get();
        return items.reduce((total, item) => total + (item.price * item.quantity), 0);
      }
    }),
    {
      name: 'cart-storage'
    }
  )
);
