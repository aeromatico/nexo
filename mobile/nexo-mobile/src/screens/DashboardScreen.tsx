import React, { useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { getDashboardData } from '../services/api';

export default function DashboardScreen({ navigation }: any) {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardData,
  });

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text>Cargando...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard</Text>
        <Text style={styles.subtitle}>Bienvenido a Nexo ERP</Text>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>Bs. {data?.total_purchases || 0}</Text>
          <Text style={styles.statLabel}>Total Compras</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{data?.pending_orders || 0}</Text>
          <Text style={styles.statLabel}>Pedidos Pendientes</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{data?.pending_invoices || 0}</Text>
          <Text style={styles.statLabel}>Facturas Pendientes</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{data?.open_tickets || 0}</Text>
          <Text style={styles.statLabel}>Soporte Abierto</Text>
        </View>
      </View>

      {/* QR Scanner Button */}
      <TouchableOpacity
        style={styles.scanButton}
        onPress={() => navigation.navigate('QRScanner')}
      >
        <Text style={styles.scanButtonText}>Escanear QR de Factura</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4472C4',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  scanButton: {
    backgroundColor: '#4472C4',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
