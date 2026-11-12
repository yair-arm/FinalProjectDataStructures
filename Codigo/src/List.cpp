#ifndef LIST_CPP
#define LIST_CPP

#include "List.h"

template <typename T>
Node<T>* List<T>::makeNode(const T& value) {
    Node<T>* newNode = new Node<T>;
    newNode->data = value;
    newNode->next = nullptr;
    return newNode;
}

template <typename T>
List<T>::List() : count(0), begin(nullptr) {}

template <typename T>
List<T>::~List() {
    clear();
}

template <typename T>
void List<T>::clear() {
    Node<T>* del = begin;
    while (del != nullptr) {
        begin = begin->next;
        delete del;
        del = begin;
    }
    count = 0;
}

template <typename T>
void List<T>::insert(int pos, const T& value) {
    if (pos < 0 || pos > count) {
        std::cout << "Error! Posicion fuera de lugar" << std::endl;
        return;
    }
    Node<T>* add = makeNode(value);
    if (pos == 0) {
        add->next = begin;
        begin = add;
    } else {
        Node<T>* cur = begin;
        for (int i = 0; i < pos - 1; i++) {
            cur = cur->next;
        }
        add->next = cur->next;
        cur->next = add;
    }
    count++;
}

template <typename T>
void List<T>::erase(int pos) {
    if (pos < 0 || pos >= count) {
        std::cout << "Error! Posicion fuera de lugar" << std::endl;
        return;
    }
    if (pos == 0) {
        Node<T>* del = begin;
        begin = begin->next;
        delete del;
    } else {
        Node<T>* cur = begin;
        for (int i = 0; i < pos - 1; i++) {
            cur = cur->next;
        }
        Node<T>* del = cur->next;
        cur->next = del->next;
        delete del;
    }
    count--;
}

template <typename T>
T& List<T>::get(int pos) const {
    if (pos < 0 || pos >= count) {
        std::cout << "Error! Posicion fuera de lugar" << std::endl;
        assert(false);
    }
    Node<T>* cur = begin;
    for (int i = 0; i < pos; i++) {
        cur = cur->next;
    }
    return cur->data;
}

template <typename T>
void List<T>::print() const {
    if (count == 0) {
        std::cout << "Lista vacia." << std::endl;
        return;
    }
    Node<T>* cur = begin;
    while (cur != nullptr) {
        std::cout << cur->data << " -> ";
        cur = cur->next;
    }
    std::cout << "NULL" << std::endl;
}

template <typename T>
void List<T>::printReverseHelper(Node<T>* node) const {
    if (node == nullptr) {
        return;
    }
    printReverseHelper(node->next);
    std::cout << node->data << " -> ";
}

template <typename T>
void List<T>::printReverse() const {
    if (count == 0) {
        std::cout << "Lista vacia." << std::endl;
        return;
    }
    printReverseHelper(begin);
    std::cout << "NULL" << std::endl;
}

template <typename T>
int List<T>::size() const {
    return count;
}

#endif
