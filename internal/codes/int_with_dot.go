package codes

import (
	"fmt"
	"strconv"

	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

type intWithDot int64

func (i *intWithDot) UnmarshalDynamoDBAttributeValue(av types.AttributeValue) error {
	var s string
	if err := attributevalue.Unmarshal(av, &s); err != nil {
		return err
	}

	u, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		return err
	}

	*i = intWithDot(u)
	return nil
}

func (i intWithDot) MarshalDynamoDBAttributeValue() (types.AttributeValue, error) {
	return &types.AttributeValueMemberN{Value: fmt.Sprintf("%d.0", int64(i))}, nil
}
