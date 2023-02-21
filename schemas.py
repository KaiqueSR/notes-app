from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    id = fields.Str(dump_only=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(PlainUserSchema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)


class UserLoginSchema(PlainUserSchema):
    username = fields.Str()
    email = fields.Str()
