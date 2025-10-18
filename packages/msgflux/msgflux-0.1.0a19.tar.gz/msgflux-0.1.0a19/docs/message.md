### **Message**

The `msgflux.Message` class, inspired by `torch.Tensor`, and implements on top of 'dotdict', was designed to facilitate the flow of information in computational graphs created with `nn` modules.

One of the central principles of its design is to allow each Module to have specific permissions to read and write to predefined fields of the Message.

This provides an organized structure for the flow of data between different components of a system.

The class implements the `set` and `get` methods, which allow creating and accessing data in the Message through strings, offering a flexible and intuitive interface. In addition, default fields are provided to structure the data in a consistent way.

`Message` is integrated into built-in `Modules` so that you *declare* how the module should read and write information.

```python
msg = mf.Message()
print(msg)
```

Each message receives an `user_id`, `user_name` and `chat_id`.Message auto generates an `execution_id`. 

```python
msg_metadata = mf.Message(user_id="123", user_name="Bruce Wayne", chat_id="456")
print(msg_metadata)
```

```python
# ways to insert data
msg.content = "Hello World!"
print(msg)
```

```python
# access values
print(msg.texts.inputs)
```

```python
# or
msg.get("texts.inputs")
```