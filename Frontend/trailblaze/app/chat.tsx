import React, { useState, useRef, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  SafeAreaView, 
  TextInput, 
  TouchableOpacity, 
  FlatList, 
  KeyboardAvoidingView, 
  Platform,
  Keyboard
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { useRouter } from 'expo-router';

type Message = {
  id: string;
  text: string;
  isUser: boolean;
};

export default function ChatScreen() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Hello! How can I help you with your routes today?', isUser: false }
  ]);
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const router = useRouter();
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    const keyboardDidShowListener = Keyboard.addListener(
      'keyboardDidShow',
      () => {
        setKeyboardVisible(true);
        scrollToBottom();
      }
    );
    const keyboardDidHideListener = Keyboard.addListener(
      'keyboardDidHide',
      () => {
        setKeyboardVisible(false);
      }
    );

    return () => {
      keyboardDidShowListener.remove();
      keyboardDidHideListener.remove();
    };
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    if (flatListRef.current && messages.length > 0) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  };

  const handleSend = () => {
    if (message.trim() === '') return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      isUser: true
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setMessage('');
    
    // Simulate bot response (echo back)
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: message, // Echo back the same message
        isUser: false
      };
      setMessages(prevMessages => [...prevMessages, botMessage]);
    }, 500);
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[
      styles.messageBubble,
      item.isUser ? styles.userMessage : styles.botMessage
    ]}>
      <Text style={[
        styles.messageText,
        item.isUser && { color: '#fff' }
      ]}>
        {item.text}
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Chat with RouteBot</Text>
      </View>
      
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoid}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          contentContainerStyle={[
            styles.messageList,
            keyboardVisible && { paddingBottom: 10 }
          ]}
          onContentSizeChange={scrollToBottom}
        />
        
        <View style={styles.inputContainer}>
          <TextInput
            style={[
              styles.input,
              { maxHeight: 100 }
            ]}
            value={message}
            onChangeText={setMessage}
            placeholder="Type a message..."
            placeholderTextColor="#999"
            multiline
            onFocus={scrollToBottom}
          />
          <TouchableOpacity 
            style={[styles.sendButton, !message.trim() && styles.sendButtonDisabled]} 
            onPress={handleSend}
            disabled={!message.trim()}
          >
            <IconSymbol size={24} name="arrow.up.circle.fill" color={message.trim() ? "#8900e1" : "#ccc"} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  keyboardAvoid: {
    flex: 1,
  },
  messageList: {
    padding: 16,
    flexGrow: 1,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    marginBottom: 12,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#8900e1',
    borderBottomRightRadius: 4,
  },
  botMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f0f0f0',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  input: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 16,
  },
  sendButton: {
    marginLeft: 12,
    padding: 4,
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
}); 