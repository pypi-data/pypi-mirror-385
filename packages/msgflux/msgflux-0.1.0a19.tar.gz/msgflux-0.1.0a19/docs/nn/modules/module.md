### **Module**

**Main features**:

* Advanced param serialization

* Update params with zero reload

* Built-in atomic Modules for fast workflow build

* OpenTelemetry integration

* Async interface (`.acall`). The module will look for an implementation of `aforward`, if it doesn't find one it will direct to `forward`.

Similar pytorch API. Advanced state_dict. Able to create/update components in runtime. Each buffer or parameter is registred in state dict.

```python
class Workflow(nn.Module):

    def __init__(self):
        super().__init__()
        self.instructions = nn.Parameter("<param_content>", "<spec>") # will can be optimized
        self.register_buffer("expected_output", "<expected_output>")

print(Workflow().state_dict())
# {'instructions': '<param_content>', 'expected_output': '<expected_output>'}
```

Logic is difined in 'forward', able hooks pre and post forward.

```python
class Model(nn.Module):

    def __init__(self):
        super().__init__()
        self.register_buffer("response", "Yes I did.")

    def forward(self, x, **kwargs):
        user_name = kwargs.get("user_name", None)
        if user_name:
            model_response = " Hi " + user_name + self.response
        else:
            model_response = self.response
        x = x + model_response
        return x

def retrieve_user_name(user_id: str):
    if user_id == "123":
        return "Clark"
    return None

def pre_hook(module, args, kwargs):
    # enhance context
    if kwargs.get("user_id"):
        user_name = retrieve_user_name(kwargs["user_id"])
        kwargs["user_name"] = user_name
    return args, kwargs

def post_hook(module, args, kwargs, output):
    print(f"inpect output: {output}")
    return output

model = Model()

# hooks returns a handle object
pre_hook_handle = model.register_forward_pre_hook(pre_hook)
post_hook_handle = model.register_forward_hook(post_hook)

print(model._forward_pre_hooks)
print(model._forward_hooks)
```

```python
input_x = "You did the work?"
kwargs = {"user_id": "123"}
result = model(input_x, **kwargs)
print(f"Output: {result}")
```

```python
# remove hooks (optional)
pre_hook_handle.remove()
post_hook_handle.remove()

result_without_hooks = model(input_x, **kwargs)
print(result_without_hooks)
```

```python
# save state dict
mf.save(model.state_dict(), "state_dict.json")

# update param
state_dict["response"] = "No, I didn't."

# update model state dict
model.load_state_dict(state_dict)

input_x = "You did the work?"
kwargs = {"user_id": "123"}
result = model(input_x, **kwargs)
print(f"Output: {result}")
```