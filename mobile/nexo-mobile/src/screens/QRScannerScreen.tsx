import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import QRCodeScanner from 'react-native-qrcode-scanner';
import { RNCamera } from 'react-native-camera';
import { verifyInvoiceQR } from '../services/api';

export default function QRScannerScreen({ navigation }: any) {
  const [scanning, setScanning] = useState(true);

  const onSuccess = async (e: any) => {
    setScanning(false);

    try {
      const result = await verifyInvoiceQR(e.data);

      if (result.valid) {
        navigation.navigate('Invoices', {
          invoiceId: result.invoice_id,
        });
      } else {
        Alert.alert('Error', 'QR inválido o factura no encontrada');
        setScanning(true);
      }
    } catch (error) {
      Alert.alert('Error', 'No se pudo verificar el QR');
      setScanning(true);
    }
  };

  return (
    <View style={styles.container}>
      <QRCodeScanner
        onRead={onSuccess}
        reactivate={scanning}
        reactivateTimeout={3000}
        flashMode={RNCamera.Constants.FlashMode.auto}
        topContent={
          <Text style={styles.centerText}>
            Escanea el código QR de tu factura
          </Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerText: {
    flex: 1,
    fontSize: 18,
    padding: 32,
    color: '#777',
  },
});
