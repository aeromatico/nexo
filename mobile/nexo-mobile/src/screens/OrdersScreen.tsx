import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { getOrders } from '../services/api';

export default function OrdersScreen() {
  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: getOrders,
  });

  const renderOrder = ({ item }: any) => (
    <View style={styles.orderCard}>
      <Text style={styles.orderNumber}>{item.name}</Text>
      <Text style={styles.customer}>{item.customer}</Text>
      <Text style={styles.status}>{item.status}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      {isLoading ? (
        <Text>Cargando...</Text>
      ) : orders.length > 0 ? (
        <FlatList
          data={orders}
          renderItem={renderOrder}
          keyExtractor={(item) => item.name}
          contentContainerStyle={styles.list}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Sin pedidos</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  list: {
    padding: 16,
  },
  orderCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  orderNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  customer: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  status: {
    fontSize: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    backgroundColor: '#e0e0e0',
    alignSelf: 'flex-start',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});
