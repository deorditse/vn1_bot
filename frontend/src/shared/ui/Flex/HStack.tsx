import {Flex, type FlexProps} from './Flex';

type HStackProps = Omit<FlexProps, 'direction'>;

export function HStack(props: HStackProps) {
  return <Flex direction="row" {...props} />;
}
