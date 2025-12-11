import React from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { getInvoices } from '../services/api';

export default function InvoicesScreen({ navigation }: any) {
  const { data: invoices = [], isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: getInvoices,
  });

  const renderInvoice = ({ item }: any) => (
    <TouchableOpacity
      style={styles.invoiceCard}
      onPress={() => navigation.navigate('InvoiceDetail', { invoiceId: item.name })}
    >
      <View>
        <Text style={styles.invoiceNumber}>{item.number}</Text>
        <Text style={styles.invoiceDate}>
          {new Date(item.date).toLocaleDateString()}
        </Text>
      </View>
      <View style={styles.invoiceAmount}>
        <Text style={styles.amount}>Bs. {item.amount}</Text>
        <Text style={[styles.status, item.status === 'paid' && styles.statusPaid]}>
          {item.status}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {isLoading ? (
        <Text>Cargando...</Text>
      ) : invoices.length > 0 ? (
        <FlatList
          data={invoices}
          renderItem={renderInvoice}
          keyExtractor={(item) => item.name}
          contentContainerStyle={styles.list}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Sin facturas</Text>
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
  invoiceCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  invoiceNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  invoiceDate: {
    fontSize: 12,
    color: '#666',
  },
  invoiceAmount: {
    alignItems: 'flex-end',
  },
  amount: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  status: {
    fontSize: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    backgroundColor: '#e0e0e0',
  },
  statusPaid: {
    backgroundColor: '#c8e6c9',
    color: '#2e7d32',
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
